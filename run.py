import re
import os
import roman  # This module handles Roman to Arabic numeral conversion

def sanitize_filename(filename):
    """ Sanitize the filename by removing or replacing invalid characters. """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename[:255]  # Truncate to max common filename length if needed

def format_to_aiken(content):
    """ Convert the content to AIKEN format and return as a string. """
    formatted_content = ""
    questions = re.findall(r'(?m)^\s*(.*?)\s*\nA\s+(.*?)\s*\nB\s+(.*?)\s*\nC\s+(.*?)\s*\nD\s+(.*?)\s*\nANSWER:\s+([A-D])', content)
    for question in questions:
        question_text = question[0].strip()
        options = question[1:5]
        answer = question[5]
        formatted_content += question_text + '\n'
        for index, option in enumerate(options):
            formatted_content += f"{chr(65+index)}) {option.strip()}\n"
        formatted_content += f"ANSWER: {answer}\n\n"
    return formatted_content

def roman_to_arabic(roman_num):
    """ Convert Roman numeral to Arabic numeral. Returns original if not a valid Roman numeral. """
    try:
        return str(roman.fromRoman(roman_num.upper()))
    except roman.InvalidRomanNumeralError:
        return roman_num

def parse_text_file(input_file_path):
    # Regex for parts and chapters
    part_pattern = re.compile(r'(?mi)^PARTE\s+([IVXLCDM\d]+)')
    chapter_pattern = re.compile(r'(?mi)^CAP[.\s]*([IVXLCDM\d]+)')

    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    parts = part_pattern.split(content)[1:]  # Split content into parts

    current_part_number = 0
    for i in range(0, len(parts), 2):
        part_number = roman_to_arabic(parts[i].strip())
        current_part_number = part_number  # Store current part number for filenames
        part_content = parts[i+1]  # Part content

        # Process each chapter in the current part
        chapters = chapter_pattern.split(part_content)[1:]
        headings = chapter_pattern.findall(part_content)

        for j in range(0, len(chapters), 2):
            chapter_number = roman_to_arabic(headings[j//2].strip())
            chapter_content = chapters[j+1].strip()
            
            filename = f'part_{current_part_number}_chapter_{chapter_number}.txt'
            increment = 0
            original_filename = filename
            while os.path.exists(filename):
                increment += 1
                filename = f"{original_filename[:-4]}{chr(96+increment)}.txt"

            # Format the chapter content to AIKEN and write to a file
            aiken_content = format_to_aiken(chapter_content)
            if aiken_content.strip():  # Ensure we don't write empty files
                with open(filename, 'w', encoding='utf-8') as chapter_file:
                    chapter_file.write(aiken_content)
            else:
                print(f"No valid questions found in part {current_part_number} chapter {chapter_number}, skipping file generation.")

# Example usage
parse_text_file('civile.txt')
