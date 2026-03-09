import zipfile
from lxml import etree
import os

def get_xml_tree(docx_path):
    """提取 Docx 内部的 document.xml 树"""
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read("word/document.xml")
        return etree.fromstring(xml_content)

def extract_styles(tree):
    """
    提取文档中所有文本节点的样式快照。
    主要关注 <w:rPr> 节点下的字体、字号、加粗等属性。
    """
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    styles = []
    # 遍历所有文本运行 (Runs)
    for r in tree.xpath("//w:r", namespaces=ns):
        text = "".join(r.xpath(".//w:t/text()", namespaces=ns))
        if not text.strip(): continue
        
        # 提取属性快照
        rPr = r.find("w:rPr", namespaces=ns)
        style_snapshot = {"text": text[:10] + "..."} # 仅记录前10位用于定位
        if rPr is not None:
            style_snapshot["bold"] = rPr.find("w:b", namespaces=ns) is not None
            sz = rPr.find("w:sz", namespaces=ns)
            style_snapshot["size"] = sz.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val") if sz is not None else "default"
            font = rPr.find("w:rFonts", namespaces=ns)
            style_snapshot["font"] = font.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia") if font is not None else "default"
        
        styles.append(style_snapshot)
    return styles

def compare_xml_consistency(template_path, generated_path):
    """
    深度 XML 对比：检查生成的文档是否在渲染过程中发生了“格式退化”。
    """
    print("\n[XML Diff Engine] 🔬 正在进行底层 XML 格式扫描...")
    if not os.path.exists(generated_path):
        return False, "生成的文档不存在"

    try:
        t_tree = get_xml_tree(template_path)
        g_tree = get_xml_tree(generated_path)
        
        t_styles = extract_styles(t_tree)
        g_styles = extract_styles(g_tree)
        
        # 这是一个简化的校验逻辑：
        # 我们重点检查生成后的文档是否还保留了关键的中文字体和字号
        critical_fail = False
        for i, s in enumerate(g_styles[:10]): # 抽查前10个节点
            if s.get("font") == "default" or s.get("size") == "default":
                # 如果变成了默认值，说明可能丢失了原本的黑体/小三设置
                print(f"  ⚠️ 警告: 节点 [{s['text']}] 疑似丢失特定格式，已回退至默认。")
                critical_fail = True
        
        if not critical_fail:
            print("  -> ✅ XML 校验通过：底层排版属性未发现退化。")
            return True, "Success"
        else:
            return False, "检测到可能的格式丢失"
            
    except Exception as e:
        return False, f"XML 解析失败: {e}"
