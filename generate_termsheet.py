# generate_termsheet.py
"""
Autocallable Structured Product Termsheet Generator
自动从定价结果生成产品说明书（支持TXT和PDF格式）
"""

import os
from datetime import datetime
from config import S0, barrier_out, barrier_in, coupon_rate, tenor_years, n_obs, sigma, r


# ==================== 数据获取函数 ====================

def get_termsheet_data(results, greeks, scenario_df):
    """
    从定价结果中提取Termsheet所需的所有数据
    """
    return {
        # 产品基本信息
        'generated_date': datetime.now().strftime('%Y-%m-%d'),
        'underlying_price': f"{S0:.2f}",
        'tenor': f"{tenor_years} Years",
        'coupon_rate': f"{coupon_rate * 100:.2f}% p.a.",
        'coupon_quarterly': f"{coupon_rate / 4 * 100:.2f}%",
        'barrier_out': f"{barrier_out * 100:.0f}%",
        'barrier_in': f"{barrier_in * 100:.0f}%",
        'n_obs': str(n_obs),

        # 定价结果
        'fair_value': f"{results['fair_value']:.4f}",
        'ko_prob': f"{results['knock_out_prob'] * 100:.2f}%",
        'ki_prob': f"{results['knock_in_prob'] * 100:.2f}%",

        # Greeks
        'delta': f"{greeks['delta']:.4f}",
        'gamma': f"{greeks['gamma']:.4f}",
        'vega': f"{greeks['vega']:.4f}",
        'rho': f"{greeks['rho']:.4f}",

        # 情景分析（取前5行）
        'scenario_table': scenario_df.head(7).to_string(index=False) if scenario_df is not None else "N/A",

        # 市场参数
        'volatility': f"{sigma * 100:.2f}%",
        'risk_free_rate': f"{r * 100:.2f}%",
    }


# ==================== Termsheet 生成器 ====================

def generate_termsheet_txt(data):
    """
    生成纯文本格式的Termsheet（保证在任何环境下都能查看）
    """
    border = "═" * 70
    dash = "─" * 70

    content = f"""
{border}
                    AUTOCALLABLE STRUCTURED NOTE
                Linked to Hang Seng Index (HSI)
                    {data['tenor']} Tenor | Quarterly Observation
{border}

1. PRODUCT SUMMARY
{dash}
Issuer               : [Bank Name] Hong Kong Branch
Product Type         : Equity-Linked Structured Note with Autocallable Feature
Underlying Asset     : Hang Seng Index (HSI) - Bloomberg Ticker: HSI <Index>
Currency             : HKD
Tenor                : {data['tenor']}
Principal Amount     : HKD 1,000,000 per Note (minimum subscription)
Issue Date           : [TBD]
Maturity Date        : [TBD] ({data['tenor']} from Issue Date)
Initial Level        : Official closing level of HSI on Issue Date
Current Level (S₀)   : {data['underlying_price']} (as of {data['generated_date']})
Observation Dates    : Quarterly ({data['n_obs']} observations in total)

{dash}

2. COUPON & PAYOFF MECHANISM
{dash}
Coupon Rate          : {data['coupon_rate']} (paid quarterly, i.e., {data['coupon_quarterly']} per quarter)

┌────────────────────┬────────────────────┬──────────────────────────────┐
│ Observation        │ Status             │ Payoff per HKD 100 Notional  │
│ Frequency          │                    │                              │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ Quarterly          │ Knock-Out          │ 100 + accrued coupon         │
│ (8 in total)       │ (≥ {data['barrier_out']} of       │ ({data['coupon_quarterly']} per quarter)  │
│                    │  Initial Level)    │ → Note matures early         │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ At Maturity        │ No Knock-Out       │ 100 + {coupon_rate * tenor_years:.0f}%          │
│                    │ No Knock-In        │ (full {data['tenor']} coupon)           │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ At Maturity        │ No Knock-Out       │ 100 × (Final Level / Initial │
│                    │ Knock-In           │ Level) → Principal loss      │
│                    │ (≤ {data['barrier_in']} of        │ possible                      │
│                    │  Initial Level)    │                              │
└────────────────────┴────────────────────┴──────────────────────────────┘

{dash}

3. KEY DEFINITIONS
{dash}
Knock-Out Event     : On any Observation Date, the official closing 
                      level of HSI ≥ {data['barrier_out']} of Initial Level.

Knock-In Event      : On any scheduled trading day during the 
                      Observation Period, the official closing level 
                      of HSI ≤ {data['barrier_in']} of Initial Level.

Observation Period  : From Issue Date to Maturity Date (inclusive).

{dash}

4. INDICATIVE PRICING (as of {data['generated_date']})
{dash}
Underlying Price (S₀)     : {data['underlying_price']}
Implied Volatility (σ)    : {data['volatility']}
Risk-Free Rate (r)        : {data['risk_free_rate']}
────────────────────────────────────────────────────────────────────
│ Metric                             │ Value                     │
├────────────────────────────────────┼───────────────────────────┤
│ Fair Value (per HKD 100 notional)  │ {data['fair_value']}      │
│ Knock-Out Probability              │ {data['ko_prob']}         │
│ Knock-In Probability               │ {data['ki_prob']}         │
└────────────────────────────────────┴───────────────────────────┘

{dash}

5. KEY GREEKS EXPOSURE (indicative)
{dash}
│ Greek  │ Definition                             │ Value       │
├────────┼────────────────────────────────────────┼─────────────┤
│ Delta  │ Price change per 1% move in HSI        │ {data['delta']} │
│ Gamma  │ Rate of change of Delta                │ {data['gamma']} │
│ Vega   │ Price change per 1% move in volatility │ {data['vega']}  │
│ Rho    │ Price change per 1% move in interest   │ {data['rho']}   │
└────────┴────────────────────────────────────────┴─────────────┘

⚠️ Key Insight: Vega is typically NEGATIVE for Autocallable structures.
   Higher volatility → Higher Knock-In probability → Lower Note value.

{dash}

6. SCENARIO ANALYSIS (illustrative)
{dash}
{data['scenario_table']}

{dash}

7. IMPORTANT DISCLAIMERS
{dash}
This document is for informational and educational purposes only 
and does not constitute an offer, solicitation, or recommendation 
to purchase or sell any financial instrument. The pricing and 
scenario figures shown are indicative only and may change based 
on market conditions.

Past performance is not indicative of future results. Investors 
should read the final offering documents and consult their own 
professional advisors before making any investment decision.

{dash}
                    FOR INTERNAL / EDUCATIONAL USE ONLY
                           [Generated on: {data['generated_date']}]
{border}
"""
    return content


# ==================== PDF 生成器（可选） ====================

def generate_termsheet_pdf(data, txt_content, output_path="outputs/Termsheet.pdf"):
    """
    使用 reportlab 生成 PDF 格式的 Termsheet
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.fonts import addMapping
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        # 注册中文字体（可选）
        try:
            pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
            pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))
        except:
            pass  # 如果没有中文字体，继续用英文

        # 创建PDF文档
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                rightMargin=2 * cm, leftMargin=2 * cm,
                                topMargin=2 * cm, bottomMargin=2 * cm)

        styles = getSampleStyleSheet()

        # 自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=12,
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            spaceBefore=12,
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4,
        )

        # 构建内容
        story = []

        # 标题
        story.append(Paragraph("AUTOCALLABLE STRUCTURED NOTE", title_style))
        story.append(Paragraph("Linked to Hang Seng Index (HSI)", body_style))
        story.append(Paragraph(f"{data['tenor']} Tenor | Quarterly Observation", body_style))
        story.append(Spacer(1, 0.5 * cm))

        # 将txt内容按行拆分，添加到PDF
        lines = txt_content.split('\n')
        for line in lines:
            if line.startswith('═') or line.startswith('─'):
                story.append(Paragraph("─" * 80, body_style))
            elif line.strip().startswith('1.') or line.strip().startswith('2.') or \
                    line.strip().startswith('3.') or line.strip().startswith('4.') or \
                    line.strip().startswith('5.') or line.strip().startswith('6.') or \
                    line.strip().startswith('7.'):
                story.append(Paragraph(line.strip(), heading_style))
            elif line.strip() and not line.strip().startswith('│') and not line.strip().startswith('┌') and \
                    not line.strip().startswith('├') and not line.strip().startswith('└') and \
                    not line.strip().startswith('┐') and not line.strip().startswith('┘') and \
                    not line.strip().startswith('┴') and not line.strip().startswith('┬') and \
                    not line.strip().startswith('┼') and not line.strip().startswith('─'):
                # 普通文本
                story.append(Paragraph(line.strip(), body_style))
            elif line.strip().startswith('│'):
                # 表格行，用等宽字体
                story.append(Paragraph(f"<pre>{line.strip()}</pre>", body_style))
            else:
                # 表格边框线，跳过或简化
                pass

        # 构建PDF
        doc.build(story)
        print(f"✅ PDF Termsheet generated: {output_path}")
        return True

    except ImportError:
        print("⚠️ reportlab not installed. Skipping PDF generation.")
        print("   Install with: pip install reportlab")
        return False
    except Exception as e:
        print(f"⚠️ PDF generation failed: {e}")
        return False

# ==================== 主函数 ====================
def generate_full_termsheet(results, greeks, scenario_df):
    """一键生成Termsheet（TXT + PDF）"""
    os.makedirs('outputs', exist_ok=True)

    data = get_termsheet_data(results, greeks, scenario_df)

    # 生成TXT
    txt_content = generate_termsheet_txt(data)
    txt_path = "outputs/Termsheet.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    print(f"✅ TXT Termsheet generated: {txt_path}")

    # 生成PDF（即使失败也不影响）
    pdf_path = "outputs/Termsheet.pdf"
    print("🔄 Attempting to generate PDF...")  # 👈 添加这行调试
    try:
        result = generate_termsheet_pdf(data, txt_content, pdf_path)  # 👈 接收返回值
        if result:
            print(f"✅ PDF Termsheet generated: {pdf_path}")
        else:
            print(f"⚠️ PDF generation returned False")
    except Exception as e:
        print(f"⚠️ PDF generation skipped with exception: {e}")  # 👈 打印具体异常
        import traceback
        traceback.print_exc()  # 👈 打印完整堆栈
# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 如果单独运行此文件，生成示例Termsheet
    print("📄 Running Termsheet generator demo...")
    print("⚠️ Please run main.py first to get pricing results.")
    print("   Or use this script with existing results.")