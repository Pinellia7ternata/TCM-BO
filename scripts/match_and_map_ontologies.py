#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
匹配TCM_BO_1.6.9.owl与fma.owl和snomed_anatomy_body_strctr.owl，并将匹配结果映射到数据属性中

Mapping pipeline (general FMA / SNOMED CT matcher) used in the TCM-BO curation series:
Ratcliff-Obershelp similarity (difflib.SequenceMatcher.ratio) on lowercased labels,
best-match selection with acceptance threshold 0.6.
"""

import xml.etree.ElementTree as ET
import os
import re
from difflib import SequenceMatcher

class OntologyMatcher:
    def __init__(self):
        self.tcm_ontology = None
        self.fma_ontology = None
        self.snomed_ontology = None
        self.tcm_namespaces = {}
        self.fma_namespaces = {}
        self.snomed_namespaces = {}
    
    def load_ontology(self, file_path):
        """
        加载本体文件
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 提取命名空间
            namespaces = {}
            for prefix, uri in root.attrib.items():
                if prefix.startswith('xmlns:'):
                    namespaces[prefix[6:]] = uri
                elif prefix == 'xmlns':
                    namespaces[''] = uri
            
            # 确保必要的命名空间存在
            if 'owl' not in namespaces:
                namespaces['owl'] = 'http://www.w3.org/2002/07/owl#'
            if 'rdfs' not in namespaces:
                namespaces['rdfs'] = 'http://www.w3.org/2000/01/rdf-schema#'
            if 'rdf' not in namespaces:
                namespaces['rdf'] = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
            
            return root, namespaces
        except Exception as e:
            print(f"加载本体文件失败: {e}")
            return None, {}
    
    def load_all_ontologies(self):
        """
        加载所有需要的本体文件
        """
        print("开始加载本体文件...")
        
        # 加载TCM本体
        tcm_file = "TCM_BO_1.6.9.owl"
        self.tcm_ontology, self.tcm_namespaces = self.load_ontology(tcm_file)
        if not self.tcm_ontology:
            print(f"无法加载TCM本体文件: {tcm_file}")
            return False
        print(f"成功加载TCM本体文件: {tcm_file}")
        
        # 加载FMA本体
        fma_file = "fma.owl"
        self.fma_ontology, self.fma_namespaces = self.load_ontology(fma_file)
        if not self.fma_ontology:
            print(f"无法加载FMA本体文件: {fma_file}")
            return False
        print(f"成功加载FMA本体文件: {fma_file}")
        
        # 加载SNOMED本体
        snomed_file = "snomed_anatomy_body_strctr.owl"
        self.snomed_ontology, self.snomed_namespaces = self.load_ontology(snomed_file)
        if not self.snomed_ontology:
            print(f"无法加载SNOMED本体文件: {snomed_file}")
            return False
        print(f"成功加载SNOMED本体文件: {snomed_file}")
        
        return True
    
    def extract_fma_concepts(self):
        """
        提取FMA本体中的概念
        """
        fma_concepts = {}
        if not self.fma_ontology:
            return fma_concepts
        
        # 查找所有类
        classes = self.fma_ontology.findall(".//owl:Class", self.fma_namespaces)
        
        for cls in classes:
            # 获取概念URI
            cls_uri = cls.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
            if not cls_uri:
                continue
            
            # 查找FMA ID
            fma_id = ""
            for elem in cls.iter():
                if 'FMAID' in elem.tag or '{http://purl.org/sig/ont/fma/}FMAID' in elem.tag:
                    fma_id = elem.text
                    break
            
            # 查找标签
            label = ""
            for label_elem in cls.findall(".//rdfs:label", self.fma_namespaces):
                label = label_elem.text
                break
            
            if fma_id:
                fma_concepts[fma_id] = {
                    'uri': cls_uri,
                    'label': label
                }
        
        print(f"成功提取 {len(fma_concepts)} 个FMA概念")
        return fma_concepts
    
    def extract_snomed_concepts(self):
        """
        提取SNOMED本体中的概念
        """
        snomed_concepts = {}
        if not self.snomed_ontology:
            return snomed_concepts
        
        # 查找所有类
        classes = self.snomed_ontology.findall(".//owl:Class", self.snomed_namespaces)
        
        for cls in classes:
            # 获取概念URI
            cls_uri = cls.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
            if not cls_uri:
                continue
            
            # 查找SNOMED ID
            snomed_id = ""
            for elem in cls.iter():
                if 'SNOMEDID' in elem.tag or '{http://ihtsdo.org/snomedct/anatomy#}SNOMEDID' in elem.tag:
                    snomed_id = elem.text
                    break
            
            # 查找标签
            label = ""
            for label_elem in cls.findall(".//rdfs:label", self.snomed_namespaces):
                label = label_elem.text
                break
            
            if snomed_id:
                snomed_concepts[snomed_id] = {
                    'uri': cls_uri,
                    'label': label
                }
        
        print(f"成功提取 {len(snomed_concepts)} 个SNOMED概念")
        return snomed_concepts
    
    def match_and_map(self):
        """
        匹配概念并映射到TCM本体的实例中
        """
        print("开始匹配和映射过程...")
        
        if not self.tcm_ontology or not self.fma_ontology or not self.snomed_ontology:
            print("本体文件未完全加载，无法进行匹配")
            return False
        
        # 提取FMA和SNOMED概念
        print("提取FMA概念...")
        fma_concepts = self.extract_fma_concepts()
        print(f"提取SNOMED概念...")
        snomed_concepts = self.extract_snomed_concepts()
        
        print(f"FMA概念数量: {len(fma_concepts)}")
        print(f"SNOMED概念数量: {len(snomed_concepts)}")
        
        # 查找TCM本体中的实例
        print("查找TCM实例...")
        instances = self.tcm_ontology.findall(".//owl:NamedIndividual", self.tcm_namespaces)
        print(f"找到 {len(instances)} 个TCM实例")
        
        if not instances:
            print("未找到TCM实例，映射过程终止")
            return False
        
        # 为每个实例添加映射信息
        mapped_count = 0
        added_snomed_mappings = 0
        added_fma_mappings = 0
        
        print("开始处理实例映射...")
        for i, instance in enumerate(instances):
            instance_uri = instance.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
            if not instance_uri:
                continue
            
            # 查找实例的标签
            instance_label = ""
            for label in instance.findall(".//rdfs:label", self.tcm_namespaces):
                if label.get('{http://www.w3.org/XML/1998/namespace}lang') == 'zh-cn':
                    instance_label = label.text
                    break
            if not instance_label:
                for label in instance.findall(".//rdfs:label", self.tcm_namespaces):
                    instance_label = label.text
                    break
            
            # 查找并更新SNOMED映射
            has_snomed = False
            for elem in instance.iter():
                if 'SNOMEDID' in elem.tag or 'SNOMEDID_data' in elem.tag:
                    has_snomed = True
                    break
            
            # 查找并更新FMA映射
            has_fma = False
            for elem in instance.iter():
                if 'FMAID' in elem.tag or 'FMAID_data' in elem.tag:
                    has_fma = True
                    break
            
            # 如果没有映射，尝试添加
            if not has_snomed and instance_label:
                print(f"尝试为实例 '{instance_label}' 匹配SNOMED概念...")
                # 尝试根据标签匹配SNOMED概念
                matched_snomed = self._match_concept_by_label(instance_label, snomed_concepts)
                if matched_snomed:
                    print(f"成功匹配SNOMED概念: {matched_snomed} - {snomed_concepts[matched_snomed]['label']}")
                    # 添加SNOMED ID数据属性
                    snomed_id = matched_snomed
                    snomed_data_prop = ET.SubElement(instance, '{http://OntoTCM.org.cn/ontologies/TCM_TO/}SNOMEDID_data')
                    snomed_data_prop.text = snomed_id
                    
                    # 添加SNOMED名称数据属性
                    snomed_name_prop = ET.SubElement(instance, '{http://OntoTCM.org.cn/ontologies/TCM_TO/}SNOMEDName_data')
                    snomed_name_prop.text = snomed_concepts[snomed_id]['label']
                    
                    added_snomed_mappings += 1
            
            if not has_fma and instance_label:
                print(f"尝试为实例 '{instance_label}' 匹配FMA概念...")
                # 尝试根据标签匹配FMA概念
                matched_fma = self._match_concept_by_label(instance_label, fma_concepts)
                if matched_fma:
                    print(f"成功匹配FMA概念: {matched_fma} - {fma_concepts[matched_fma]['label']}")
                    # 添加FMA ID数据属性
                    fma_id = matched_fma
                    fma_data_prop = ET.SubElement(instance, '{http://OntoTCM.org.cn/ontologies/TCM_TO/}FMAID_data')
                    fma_data_prop.text = fma_id
                    
                    # 添加FMA名称数据属性
                    fma_name_prop = ET.SubElement(instance, '{http://OntoTCM.org.cn/ontologies/TCM_TO/}FMAName_data')
                    fma_name_prop.text = fma_concepts[fma_id]['label']
                    
                    added_fma_mappings += 1
            
            mapped_count += 1
            if mapped_count % 10 == 0:
                print(f"已处理 {mapped_count} 个实例")
        
        print(f"完成映射处理，共处理 {mapped_count} 个实例")
        print(f"新增 {added_snomed_mappings} 个SNOMED映射")
        print(f"新增 {added_fma_mappings} 个FMA映射")
        return True
    
    def _match_concept_by_label(self, instance_label, concepts):
        """
        根据标签匹配概念
        """
        if not instance_label:
            return None
        
        # 简单的字符串匹配，实际应用中可能需要更复杂的算法
        best_match = None
        best_score = 0
        
        for concept_id, concept_info in concepts.items():
            concept_label = concept_info.get('label', '')
            if not concept_label:
                continue
            
            # 计算相似度
            score = self._calculate_similarity(instance_label, concept_label)
            if score > best_score and score > 0.6:  # 设置阈值
                best_score = score
                best_match = concept_id
        
        return best_match
    
    def _calculate_similarity(self, str1, str2):
        """
        计算两个字符串的相似度
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def save_updated_ontology(self, output_file="TCM_BO_1.6.9_mapped.owl"):
        """
        保存更新后的本体文件
        """
        print(f"开始保存更新后的本体文件: {output_file}")
        
        if not self.tcm_ontology:
            print("没有可保存的本体")
            return False
        
        try:
            # 创建ElementTree
            tree = ET.ElementTree(self.tcm_ontology)
            
            # 保存文件
            tree.write(output_file, encoding='utf-8', xml_declaration=True, default_namespace=self.tcm_namespaces.get(''))
            print(f"成功保存更新后的本体文件: {output_file}")
            print(f"文件大小: {os.path.getsize(output_file)} 字节")
            return True
        except Exception as e:
            print(f"保存本体文件失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """
    主函数
    """
    matcher = OntologyMatcher()
    
    # 加载本体
    if not matcher.load_all_ontologies():
        return
    
    # 提取概念
    fma_concepts = matcher.extract_fma_concepts()
    snomed_concepts = matcher.extract_snomed_concepts()
    
    # 进行匹配和映射
    if matcher.match_and_map():
        # 保存更新后的本体
        matcher.save_updated_ontology()
    
    print("本体匹配和映射完成!")

if __name__ == "__main__":
    main()
