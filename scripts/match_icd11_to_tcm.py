#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ICD-11 matcher used in the TCM-BO curation series: Ratcliff-Obershelp similarity
(difflib.SequenceMatcher.ratio) on cleaned labels (lowercase, punctuation stripped),
best-match selection with acceptance threshold 0.6; Chinese-name fallback when the
English-name best score is below 0.7.
"""

import pandas as pd
import xml.etree.ElementTree as ET
import re
from difflib import SequenceMatcher

# 读取Excel文档
def read_excel_data():
    print("读取Excel文档...")
    df = pd.read_excel('ICD 11 身体结构部分内容.xlsx')
    print(f"Excel文件读取成功，共{len(df)}行数据")
    
    # 提取有用的列
    icd_data = []
    for index, row in df.iterrows():
        # 提取ICD-11实体URL
        entity_url = row.iloc[0] if pd.notna(row.iloc[0]) else None
        
        # 提取英文名称
        en_name = row.iloc[4] if pd.notna(row.iloc[4]) else None
        
        # 提取中文名称
        zh_name = row.iloc[5] if pd.notna(row.iloc[5]) else None
        
        if entity_url and (en_name or zh_name):
            # 从URL中提取ICD-11 ID
            icd_id = entity_url.split('/')[-1]
            icd_data.append({
                'icd_id': icd_id,
                'entity_url': entity_url,
                'en_name': en_name,
                'zh_name': zh_name
            })
    
    print(f"提取出{len(icd_data)}条有效的ICD-11记录")
    return icd_data

# 读取中医身体结构本体
def read_tcm_ontology():
    print("\n读取中医身体结构本体...")
    tree = ET.parse('TCM_BO_1.7.0_snomed_fma_mapped_all_data_properties.owl')
    root = tree.getroot()
    
    # 手动添加必要的命名空间
    namespaces = {
        'owl': 'http://www.w3.org/2002/07/owl#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'
    }
    
    tcm_classes = []
    classes = root.findall('.//owl:Class', namespaces)
    print(f"找到{len(classes)}个中医身体结构类")
    
    for cls in classes:
        cls_uri = cls.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about')
        
        # 提取标签
        labels = []
        for label in cls.findall('.//rdfs:label', namespaces):
            text = label.text
            lang = label.get('{http://www.w3.org/XML/1998/namespace}lang')
            if text:
                labels.append((text, lang))
        
        if cls_uri and labels:
            tcm_classes.append({
                'uri': cls_uri,
                'labels': labels
            })
    
    print(f"提取出{len(tcm_classes)}个带有标签的中医身体结构类")
    return tcm_classes

# 模糊匹配函数
def fuzzy_match(icd_name, tcm_labels, threshold=0.6):
    """基于字符串相似度进行模糊匹配"""
    best_match = None
    best_score = 0
    
    for label, lang in tcm_labels:
        # 清理字符串
        icd_clean = re.sub(r'[^\w\s]', '', icd_name.lower())
        tcm_clean = re.sub(r'[^\w\s]', '', label.lower())
        
        # 计算相似度
        score = SequenceMatcher(None, icd_clean, tcm_clean).ratio()
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = (label, lang, score)
    
    return best_match

# 执行匹配
def perform_matching(icd_data, tcm_classes):
    print("\n开始执行模糊匹配...")
    matches = []
    match_count = 0
    
    for icd_item in icd_data[:100]:  # 先处理前100条数据进行测试
        icd_id = icd_item['icd_id']
        icd_entity_url = icd_item['entity_url']
        icd_en_name = icd_item['en_name']
        icd_zh_name = icd_item['zh_name']
        
        best_tcm_match = None
        best_match_score = 0
        
        # 尝试用英文名称匹配
        if icd_en_name:
            for tcm_item in tcm_classes:
                match = fuzzy_match(icd_en_name, tcm_item['labels'])
                if match and match[2] > best_match_score:
                    best_match_score = match[2]
                    best_tcm_match = tcm_item
        
        # 尝试用中文名称匹配
        if icd_zh_name and (not best_tcm_match or best_match_score < 0.7):
            for tcm_item in tcm_classes:
                match = fuzzy_match(icd_zh_name, tcm_item['labels'])
                if match and match[2] > best_match_score:
                    best_match_score = match[2]
                    best_tcm_match = tcm_item
        
        if best_tcm_match:
            matches.append({
                'icd_id': icd_id,
                'icd_entity_url': icd_entity_url,
                'icd_en_name': icd_en_name,
                'icd_zh_name': icd_zh_name,
                'tcm_uri': best_tcm_match['uri'],
                'match_score': best_match_score
            })
            match_count += 1
            
            # 打印匹配结果
            if match_count % 10 == 0:
                print(f"已匹配{match_count}条记录")
    
    print(f"\n匹配完成，共找到{match_count}条匹配记录")
    return matches

# 主函数
def main():
    # 读取数据
    icd_data = read_excel_data()
    tcm_classes = read_tcm_ontology()
    
    # 执行匹配
    matches = perform_matching(icd_data, tcm_classes)
    
    # 保存匹配结果
    if matches:
        print("\n保存匹配结果到matches.csv...")
        match_df = pd.DataFrame(matches)
        match_df.to_csv('matches.csv', index=False, encoding='utf-8-sig')
        print(f"匹配结果已保存，共{len(matches)}条记录")
    
if __name__ == "__main__":
    main()
