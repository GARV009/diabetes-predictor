"""
PDF Health Report Generator
Generates comprehensive PDF health reports for users
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.colors import HexColor, black, white, grey, whitesmoke
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
from app.utils.diet_planner import generate_diet_plan
from app.utils.health_checkup import generate_health_checkup_plan

def create_health_report_pdf(user, records, gamification=None):
    """
    Generate a comprehensive PDF health report for a user
    Returns BytesIO object containing the PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1890ff'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#096dd9'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Title
    story.append(Paragraph("HEALTH REPORT", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # User Profile Section
    story.append(Paragraph("USER PROFILE", heading_style))
    user_data = [
        ['Username', user.username],
        ['Email', user.email],
        ['Account Created', user.created_at.strftime('%B %d, %Y')],
        ['Member For', f"{(datetime.utcnow() - user.created_at).days} days"]
    ]
    
    user_table = Table(user_data, colWidths=[2*inch, 4*inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e6f7ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(user_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Gamification Stats
    if gamification:
        story.append(Paragraph("HEALTH ACHIEVEMENTS", heading_style))
        badges_earned = [
            gamification.badge_first_prediction,
            gamification.badge_week_streak,
            gamification.badge_health_champion,
            gamification.badge_diet_master,
            gamification.badge_consistency_king
        ]
        badges_count = sum(1 for b in badges_earned if b)
        
        stats_data = [
            ['Total Points', str(gamification.total_points)],
            ['Current Streak', f"{gamification.current_streak} days"],
            ['Longest Streak', f"{gamification.longest_streak} days"],
            ['Total Checkups', str(gamification.predictions_count)],
            ['Badges Earned', f"{badges_count}/5"]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 4*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#fff4e6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.3 * inch))
    
    # Health Records
    if records:
        latest = records[0]
        
        # Latest Assessment
        story.append(Paragraph("LATEST HEALTH ASSESSMENT", heading_style))
        
        prediction_text = "You don't have Diabetes." if latest.prediction_result == 0 else "You have Diabetes - please consult a doctor."
        risk_color = HexColor('#10b981') if latest.risk_level == 'Low' else HexColor('#ef4444')
        
        assessment_data = [
            ['Assessment Date', latest.created_at.strftime('%B %d, %Y at %I:%M %p')],
            ['Prediction Result', prediction_text],
            ['Risk Level', latest.risk_level]
        ]
        
        assessment_table = Table(assessment_data, colWidths=[2*inch, 4*inch])
        assessment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f9ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(assessment_table)
        story.append(Spacer(1, 0.15 * inch))
        
        # Health Metrics
        story.append(Paragraph("HEALTH METRICS", heading_style))
        metrics_data = [
            ['Metric', 'Value', 'Status'],
            ['Glucose Level', f"{latest.glucose} mg/dL", 'Normal' if latest.glucose < 100 else 'High'],
            ['Insulin', f"{latest.insulin} μU/mL", 'Normal' if latest.insulin < 166 else 'High'],
            ['BMI', f"{latest.bmi}", 'Healthy' if latest.bmi < 25 else 'Overweight' if latest.bmi < 30 else 'Obese'],
            ['Age', f"{latest.age} years", ''],
            ['Blood Pressure', f"{latest.bp_systolic}/{latest.bp_diastolic}", 'Normal' if latest.bp_systolic < 120 else 'Elevated'],
            ['Family History', 'Yes' if latest.family_history else 'No', '']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.5*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#096dd9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')])
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Diet Plan
        diet_plan = generate_diet_plan(latest.glucose, latest.insulin, latest.bmi, latest.age, latest.prediction_result)
        if diet_plan:
            story.append(Paragraph("PERSONALIZED DIET PLAN", heading_style))
            
            diet_data = [
                ['Daily Calorie Target', str(diet_plan.get('daily_calories', 'N/A')) + ' kcal'],
                ['Carbohydrates', diet_plan.get('macronutrients', {}).get('carbohydrates', 'N/A')],
                ['Protein', diet_plan.get('macronutrients', {}).get('protein', 'N/A')],
                ['Healthy Fats', diet_plan.get('macronutrients', {}).get('healthy_fats', 'N/A')]
            ]
            
            diet_table = Table(diet_data, colWidths=[2*inch, 4*inch])
            diet_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0fdf4')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(diet_table)
            
            # Foods to include/avoid
            story.append(Spacer(1, 0.15 * inch))
            story.append(Paragraph("Recommended Foods:", ParagraphStyle(
                'SubHeading',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica-Bold'
            )))
            
            if 'diabetic_friendly_foods' in diet_plan and 'vegetables' in diet_plan['diabetic_friendly_foods']:
                foods_text = ", ".join(diet_plan['diabetic_friendly_foods']['vegetables'][:5])
                story.append(Paragraph(foods_text, body_style))
            
            story.append(Spacer(1, 0.15 * inch))
        
        # Doctor Recommendations
        checkup_plan = generate_health_checkup_plan(
            latest.age, latest.bmi, latest.glucose, latest.bp_systolic, 
            latest.bp_diastolic, latest.prediction_result, latest.family_history
        )
        if checkup_plan:
            story.append(PageBreak())
            story.append(Paragraph("HEALTH CHECKUP RECOMMENDATIONS", heading_style))
            
            doc_data = [
                ['Doctor Visits', checkup_plan.get('checkup_frequency', {}).get('doctor_visits', 'N/A')],
                ['Reason', checkup_plan.get('checkup_frequency', {}).get('reason', 'N/A')]
            ]
            
            doc_table = Table(doc_data, colWidths=[2*inch, 4*inch])
            doc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#eff6ff')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(doc_table)
            
            # Essential Tests
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("Essential Blood Tests:", ParagraphStyle(
                'SubHeading',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica-Bold'
            )))
            
            if 'blood_tests' in checkup_plan and 'essential' in checkup_plan['blood_tests']:
                for test in checkup_plan['blood_tests']['essential'][:5]:
                    test_text = f"• {test.get('name', 'Test')} - {test.get('frequency', 'Regularly')} ({test.get('reason', '')})"
                    story.append(Paragraph(test_text, body_style))
        
        # Health Summary
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("HEALTH SUMMARY", heading_style))
        
        avg_glucose = sum(r.glucose for r in records) / len(records)
        avg_bmi = sum(r.bmi for r in records) / len(records)
        high_risk_count = sum(1 for r in records if r.risk_level == 'High')
        
        summary_data = [
            ['Total Checkups', str(len(records))],
            ['Average Glucose', f"{avg_glucose:.1f} mg/dL"],
            ['Average BMI', f"{avg_bmi:.1f}"],
            ['High Risk Cases', str(high_risk_count)],
            ['Success Rate', f"{((len(records) - high_risk_count) / len(records) * 100):.0f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f5f3ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(summary_table)
    
    # Footer
    story.append(Spacer(1, 0.5 * inch))
    footer_text = "This report is generated by Health Hub and should be reviewed with your healthcare provider. It is not a substitute for professional medical advice."
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=0
    )))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
