"""
Модуль для экспорта отчетов в PDF
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os
from typing import Dict, Any
import matplotlib.pyplot as plt
import io


class PDFReportGenerator:
    """Класс для генерации PDF отчетов"""

    def __init__(self, output_dir: str = "reports"):
        """
        Инициализация генератора отчетов

        Args:
            output_dir: Директория для сохранения отчетов
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()

        # Создаем кастомные стили
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

    def create_report(self, stats: Dict[str, Any], analytics, output_filename: str = None) -> str:
        """
        Создание PDF отчета

        Args:
            stats: Словарь со статистикой
            analytics: Объект SupplementAnalytics
            output_filename: Имя выходного файла

        Returns:
            Путь к созданному PDF файлу
        """
        if output_filename is None:
            output_filename = f"supplement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        filepath = os.path.join(self.output_dir, output_filename)

        # Создаем документ
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []

        # Заголовок
        title = Paragraph(
            f"ОТЧЕТ О ПРИЕМЕ БАДов<br/>{datetime.now().strftime('%d.%m.%Y')}",
            self.title_style
        )
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))

        # Общая статистика
        story.append(Paragraph("ОБЩАЯ СТАТИСТИКА", self.heading_style))

        general_data = [
            ['Показатель', 'Значение'],
            ['Всего дней отслеживания', f"{stats.get('total_days', 0)}"],
            ['Соблюдение приема Омега-3', f"{stats.get('omega3_compliance', 0):.1f}%"],
            ['Соблюдение приема Витамина D3', f"{stats.get('d3_compliance', 0):.1f}%"],
        ]

        general_table = Table(general_data, colWidths=[3.5 * inch, 2 * inch])
        general_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        story.append(general_table)
        story.append(Spacer(1, 0.3 * inch))

        # Показатели самочувствия
        story.append(Paragraph("СРЕДНИЕ ПОКАЗАТЕЛИ САМОЧУВСТВИЯ", self.heading_style))

        wellbeing_data = [
            ['Показатель', 'Средняя оценка'],
            ['Уровень энергии', f"{stats.get('avg_energy', 0):.1f}/10"],
            ['Качество сна', f"{stats.get('avg_sleep', 0):.1f}/10"],
            ['Настроение', f"{stats.get('avg_mood', 0):.1f}/10"],
        ]

        wellbeing_table = Table(wellbeing_data, colWidths=[3.5 * inch, 2 * inch])
        wellbeing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        story.append(wellbeing_table)
        story.append(Spacer(1, 0.3 * inch))

        # Дозировки
        story.append(Paragraph("СРЕДНИЕ ДОЗИРОВКИ", self.heading_style))

        dosage_data = [
            ['БАД', 'Средняя доза'],
            ['Омега-3 (EPA+DHA)', f"{stats.get('avg_omega3_dose', 0):.0f} мг"],
            ['Витамин D3', f"{stats.get('avg_d3_dose', 0):.0f} МЕ"],
        ]

        dosage_table = Table(dosage_data, colWidths=[3.5 * inch, 2 * inch])
        dosage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E67E22')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        story.append(dosage_table)
        story.append(Spacer(1, 0.3 * inch))

        # Последние анализы
        if 'last_lab_date' in stats:
            story.append(Paragraph("ПОСЛЕДНИЕ РЕЗУЛЬТАТЫ АНАЛИЗОВ", self.heading_style))

            lab_data = [
                ['Параметр', 'Значение'],
                ['Дата анализа', stats.get('last_lab_date', 'N/A')],
            ]

            if stats.get('last_vitamin_d'):
                lab_data.append(['Витамин D (25-OH)', f"{stats['last_vitamin_d']:.1f} нг/мл"])

            if stats.get('last_omega3_index'):
                lab_data.append(['Омега-3 индекс', f"{stats['last_omega3_index']:.1f}%"])

            lab_table = Table(lab_data, colWidths=[3.5 * inch, 2 * inch])
            lab_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9B59B6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))

            story.append(lab_table)

        # Строим документ
        doc.build(story)

        return filepath

    def save_plot_to_image(self, fig, filename: str) -> str:
        """
        Сохранение matplotlib графика в файл

        Args:
            fig: Figure объект matplotlib
            filename: Имя файла для сохранения

        Returns:
            Путь к сохраненному файлу
        """
        filepath = os.path.join(self.output_dir, filename)
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return filepath
