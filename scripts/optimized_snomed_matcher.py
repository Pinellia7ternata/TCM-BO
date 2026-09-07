#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的中医身体结构本体与SNOMED CT匹配脚本
改进了模糊匹配机制，考虑中医术语特点

SNOMED CT matcher with the enhanced scorer described in the TCM-BO manuscript:
exact label equality = 1.0, curated TCM synonym-table equality = 0.95,
substring containment boosted to 0.8, acceptance threshold 0.7, early stop above 0.9.
"""

import xml.etree.ElementTree as ET
import os
import re
from difflib import SequenceMatcher

class OptimizedSnomedMatcher:
    def __init__(self, tcm_file, snomed_file):
        self.tcm_file = tcm_file
        self.snomed_file = snomed_file
        
        # 命名空间
        self.namespaces = {
            'owl': 'http://www.w3.org/2002/07/owl#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'snomed': 'http://snomed.info/id/'
        }
        
        # 注册命名空间
        for prefix, uri in self.namespaces.items():
            ET.register_namespace(prefix, uri)
        
        # 存储本体数据
        self.tcm_data = {}
        self.snomed_data = {}
        
        # 存储匹配结果
        self.matches = {}
        
        # 中医术语同义词和别名映射
        self.tcm_synonyms = {
            '心': ['心脏', '心室', '心房'],
            '肝': ['肝脏', '肝叶'],
            '脾': ['脾脏'],
            '肺': ['肺脏', '肺叶'],
            '肾': ['肾脏', '肾盂'],
            '胃': ['胃部', '胃腔'],
            '肠': ['肠道', '小肠', '大肠'],
            '膀胱': ['膀胱腔'],
            '胆': ['胆囊'],
            '脑': ['大脑', '脑部'],
            '骨': ['骨骼'],
            '肌肉': ['肌'],
            '皮肤': ['皮'],
            '血管': ['脉管'],
            '神经': ['神经纤维']
        }
    
    def load_ontology(self, file_path):
        """
        加载并解析本体文件
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            print(f"✓ 成功加载文件: {os.path.basename(file_path)}")
            return tree, root
        except Exception as e:
            print(f"✗ 解析文件失败: {e}")
            return None, None
    
    def extract_entities(self, root, ontology_type):
        """
        提取本体中的类和实例
        """
        entities = {}
        
        # 提取类
        for cls in root.findall('.//owl:Class', self.namespaces):
            iri = cls.get(f"{{{self.namespaces['rdf']}}}about")
            if iri:
                labels = self.get_labels(cls)
                entities[iri] = {
                    'type': 'class',
                    'labels': labels
                }
        
        # 提取实例
        for indiv in root.findall('.//owl:NamedIndividual', self.namespaces):
            iri = indiv.get(f"{{{self.namespaces['rdf']}}}about")
            if iri:
                labels = self.get_labels(indiv)
                entities[iri] = {
                    'type': 'individual',
                    'labels': labels
                }
        
        print(f"✓ 从{ontology_type}中提取了 {len(entities)} 个实体")
        return entities
    
    def get_labels(self, element):
        """
        获取元素的所有标签
        """
        labels = {}
        for label in element.findall('./rdfs:label', self.namespaces):
            lang = label.get('{http://www.w3.org/XML/1998/namespace}lang', 'en')
            if label.text:
                labels[lang] = label.text
        return labels
    
    def get_id_from_iri(self, iri, ontology_type):
        """
        从IRI中提取ID
        """
        if not iri:
            return None
        
        if ontology_type == 'snomed':
            # SNOMED ID通常在IRI末尾
            # 匹配模式：#后跟数字
            match = re.search(r'#([0-9]+)$', iri)
            if match:
                return match.group(1)
            # 或者 / 后跟数字
            match = re.search(r'/([0-9]+)$', iri)
            if match:
                return match.group(1)
        return None
    
    def get_synonyms(self, term):
        """
        获取中医术语的同义词和别名
        """
        synonyms = [term]
        
        # 检查是否是中医术语的同义词
        for key, syns in self.tcm_synonyms.items():
            if term == key:
                synonyms.extend(syns)
            elif term in syns:
                synonyms.append(key)
        
        return synonyms
    
    def enhanced_similarity(self, str1, str2):
        """
        增强的字符串相似度计算，考虑中医术语特点
        """
        if not str1 or not str2:
            return 0
        
        # 基本相似度
        base_score = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
        
        # 检查是否有同义词匹配
        syns1 = self.get_synonyms(str1)
        syns2 = self.get_synonyms(str2)
        
        max_syn_score = base_score
        for syn1 in syns1:
            for syn2 in syns2:
                syn_score = SequenceMatcher(None, syn1.lower(), syn2.lower()).ratio()
                if syn_score > max_syn_score:
                    max_syn_score = syn_score
        
        # 检查子字符串匹配（如"心脏"包含"心"）
        sub_score = 0
        if len(str1) > 0 and len(str2) > 0:
            if str1.lower() in str2.lower() or str2.lower() in str1.lower():
                sub_score = 0.8
        
        # 综合得分
        final_score = max(max_syn_score, sub_score, base_score)
        return final_score
    
    def match_entities(self):
        """
        匹配TCM_BO中的实体与SNOMED中的实体
        """
        print("\n=== 开始匹配实体 ===")
        
        try:
            # 加载本体
            tcm_tree, tcm_root = self.load_ontology(self.tcm_file)
            snomed_tree, snomed_root = self.load_ontology(self.snomed_file)
            
            if not all([tcm_tree, snomed_tree]):
                print("✗ 无法加载所有本体文件")
                return False
            
            # 提取TCM实体
            self.tcm_data = self.extract_entities(tcm_root, "TCM_BO")
            total_tcm_entities = len(self.tcm_data)
            print(f"✓ TCM实体总数: {total_tcm_entities}")
            
            # 提取SNOMED实体并构建标签映射
            print("\n=== 处理SNOMED实体 ===")
            snomed_label_map = {}
            snomed_count = 0
            
            for cls in snomed_root.findall('.//owl:Class', self.namespaces):
                iri = cls.get(f"{{{self.namespaces['rdf']}}}about")
                if iri:
                    labels = self.get_labels(cls)
                    for lang, label in labels.items():
                        if label not in snomed_label_map:
                            snomed_label_map[label] = iri
                    snomed_count += 1
            
            print(f"✓ 处理了 {snomed_count} 个SNOMED实体，构建了 {len(snomed_label_map)} 个标签映射")
            
            # 执行匹配
            print("\n=== 执行实体匹配 ===")
            matched_count = 0
            processed_count = 0
            max_process_count = 1000  # 增加处理数量
            
            # 预处理：提取所有TCM标签
            tcm_labels = {}
            for tcm_iri, tcm_data in self.tcm_data.items():
                tcm_labels[tcm_iri] = tcm_data['labels']
            
            print(f"  开始匹配TCM实体，最多处理: {max_process_count}")
            
            for tcm_iri, labels in tcm_labels.items():
                processed_count += 1
                if processed_count > max_process_count:
                    break
                    
                if processed_count % 100 == 0:
                    print(f"  已处理 {processed_count}/{max_process_count} 个TCM实体")
                
                best_snomed_match = None
                best_snomed_score = 0
                
                # 尝试匹配每个标签
                for lang, tcm_label in labels.items():
                    # 直接查找完全匹配
                    if tcm_label in snomed_label_map:
                        best_snomed_match = snomed_label_map[tcm_label]
                        best_snomed_score = 1.0
                    
                    # 尝试同义词匹配
                    synonyms = self.get_synonyms(tcm_label)
                    for syn in synonyms:
                        if syn in snomed_label_map:
                            best_snomed_match = snomed_label_map[syn]
                            best_snomed_score = 0.95  # 同义词匹配得分
                    
                    # 如果没有完全匹配，进行相似度匹配（优化版）
                    if best_snomed_score < 0.8:
                        # 增加匹配范围
                        snomed_matches = 0
                        max_snomed_matches = 2000  # 增加匹配数量
                        
                        for snomed_label, snomed_iri in list(snomed_label_map.items())[:max_snomed_matches]:
                            snomed_matches += 1
                            score = self.enhanced_similarity(tcm_label, snomed_label)
                            if score > best_snomed_score:
                                best_snomed_score = score
                                best_snomed_match = snomed_iri
                            # 如果相似度已经很高，提前结束
                            if best_snomed_score > 0.9:
                                break
                
                # 存储匹配结果（调整阈值）
                if best_snomed_score > 0.7:  # 降低阈值，提高匹配率
                    self.matches[tcm_iri] = {
                        'snomed': {
                            'iri': best_snomed_match,
                            'score': best_snomed_score,
                            'id': self.get_id_from_iri(best_snomed_match, 'snomed') if best_snomed_match else None
                        }
                    }
                    matched_count += 1
            
            print(f"✓ 共处理了 {processed_count} 个TCM实体")
            print(f"✓ 共匹配到 {matched_count} 个实体")
            return True
        except Exception as e:
            print(f"✗ 匹配过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def map_matches_to_ontology(self, output_file):
        """
        将匹配结果映射到TCM_BO本体中
        """
        print("\n=== 开始映射匹配结果 ===")
        
        try:
            # 加载TCM_BO本体
            tcm_tree, tcm_root = self.load_ontology(self.tcm_file)
            if not tcm_tree:
                return False
            
            # 遍历所有实体，添加匹配结果
            modified_count = 0
            processed_entities = 0
            matched_entities = 0
            max_process_count = 2000  # 增加处理数量
            
            print(f"  开始遍历TCM实体，匹配结果数量: {len(self.matches)}")
            print(f"  最多处理: {max_process_count} 个实体")
            
            # 打印前5个匹配结果
            print(f"  前5个匹配结果:")
            for i, (iri, data) in enumerate(list(self.matches.items())[:5]):
                print(f"    {i+1}. {iri[:100]}...")
                print(f"      SNOMED: {data['snomed']['iri'] if data['snomed']['iri'] else 'None'}, ID: {data['snomed']['id']}, Score: {data['snomed']['score']:.3f}")
            
            for elem in tcm_root.iter():
                # 处理类和实例
                if '{http://www.w3.org/2002/07/owl#}Class' in elem.tag or '{http://www.w3.org/2002/07/owl#}NamedIndividual' in elem.tag:
                    processed_entities += 1
                    if processed_entities > max_process_count:
                        break
                        
                    iri = elem.get(f"{{{self.namespaces['rdf']}}}about")
                    
                    if processed_entities % 200 == 0:
                        print(f"  已处理 {processed_entities}/{max_process_count} 个实体")
                    
                    if iri:
                        if iri in self.matches:
                            matched_entities += 1
                            print(f"  找到匹配实体: {iri[:100]}...")
                            match_data = self.matches[iri]
                            
                            # 添加SNOMED映射
                            if match_data['snomed']['iri'] and match_data['snomed']['id']:
                                # 检查是否已存在SNOMED ID属性
                                existing_snomed_ids = elem.findall('./snomed:id', self.namespaces)
                                if not existing_snomed_ids:
                                    # 添加SNOMED ID作为数据属性
                                    snomed_id_elem = ET.SubElement(elem, f"{{{self.namespaces['snomed']}}}id")
                                    snomed_id_elem.text = match_data['snomed']['id']
                                    modified_count += 1
                                    print(f"    添加SNOMED ID: {match_data['snomed']['id']} (Score: {match_data['snomed']['score']:.3f})")
                                else:
                                    print(f"    SNOMED ID已存在，跳过")
            
            print(f"  共处理了 {processed_entities} 个实体")
            print(f"  找到 {matched_entities} 个匹配实体")
            print(f"✓ 共修改了 {modified_count} 个属性")
            
            # 保存结果
            print(f"  正在保存文件...")
            print(f"  输出文件路径: {output_file}")
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"  创建输出目录: {output_dir}")
            
            try:
                tcm_tree.write(output_file, encoding='utf-8', xml_declaration=True)
                print(f"✓ 成功保存映射结果到: {output_file}")
                if os.path.exists(output_file):
                    print(f"  文件大小: {os.path.getsize(output_file):,} 字节")
                else:
                    print(f"  文件不存在，保存失败")
                return True
            except Exception as e:
                print(f"✗ 保存文件失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        except Exception as e:
            print(f"✗ 映射过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self, output_file):
        """
        运行完整的匹配和映射流程
        """
        print("=" * 80)
        print("开始优化的本体匹配和映射流程")
        print(f"TCM_BO文件: {os.path.basename(self.tcm_file)}")
        print(f"SNOMED文件: {os.path.basename(self.snomed_file)}")
        print(f"输出文件: {os.path.basename(output_file)}")
        print("=" * 80)
        
        # 执行匹配
        if not self.match_entities():
            print("✗ 匹配失败")
            return False
        
        # 执行映射
        if not self.map_matches_to_ontology(output_file):
            print("✗ 映射失败")
            return False
        
        print("\n" + "=" * 80)
        print("✓ 优化的本体匹配和映射流程完成！")
        print("=" * 80)
        return True

if __name__ == "__main__":
    # 定义文件路径
    tcm_file = "TCM_BO_1.6.5.owl"
    snomed_file = "snomed_anatomy_body_strctr.owl"
    output_file = "TCM_BO_1.6.5_snomed_optimized_mapped.owl"
    
    # 创建匹配器实例并运行
    matcher = OptimizedSnomedMatcher(tcm_file, snomed_file)
    matcher.run(output_file)
