import os
import openai
import requests
import base64
from dotenv import load_dotenv

load_dotenv()
website = os.getenv('wp_website')
wp_user = os.getenv('wp_user')
wp_password = os.getenv('wp_password')
wp_credential = f'{wp_user}:{wp_password}'
wp_token = base64.b64encode(wp_credential.encode())
wp_header = {'Authorization': f'Basic {wp_token.decode("utf-8")}'}

keyword = input('Write down your keyword for buyer guide: ')
slug = keyword.strip().replace('', '-')
api_url = f'{website}wp-json/wp/v2/posts'
title = f'{keyword} Buyer Guide'


def create_wp_post(api, f_title, f_content, f_slug, status='draft'):
    """
    function to post on wp
    :param api:
    :param f_title:
    :param f_content:
    :param f_slug:
    :param status:
    :return:
    """
    data = {
        'title': f_title,
        'content': f_content,
        'slug': f_slug,
        'status': status
    }
    res = requests.post(api, headers=wp_header, json=data)
    if res.status_code == 201:
        print(f'{title} Article Drafted Successfully')
    else:
        print('Error occurred')


def buyer_guide(my_prompt):
    """
    function for buyer guide generation
    :param my_prompt: instructions with keyword
    :return: output
    """
    openai.api_key = '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'

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=my_prompt,
        temperature=0.7,
        max_tokens=4000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    output = response.get('choices')[0].get('text').strip('\n')
    return output


def ques_answer(data_qa):
    """
    function for question and answer
    :param data_qa: question data
    :return: answer
    """
    data_qa.strip()
    number_list = ['1. ', '2. ', '3. ', '4. ', '5. ']

    for numbers in number_list:
        data_qa = data_qa.replace(numbers, '')

    main_data_questions = data_qa.split('\n')

    while '' in main_data_questions:
        main_data_questions.remove('')

    qa_dict = {}
    for question in main_data_questions:
        qa_dict[question] = buyer_guide(question) + '\n'

    return qa_dict


def h2_heading(text_for_h2):
    """
    heading two function for wordpress
    :param text_for_h2:
    :return: heading 2
    """
    heading_2 = f'(<!-- wp:heading --><h2>{text_for_h2}</h2><!-- /wp:heading -->'
    return heading_2


def h3_heading(text_for_h3):
    """
    heading three function for wordpress
    :param text_for_h3:
    :return: heading h3
    """
    heading_3 = f'<!-- wp:heading --><h3>{text_for_h3}</h3><!-- /wp:heading -->'
    return heading_3


def paragraph(text):
    """
    paragraph function for wordpress
    :param text:
    :return: paragraph
    """
    paragraph = f'<!-- wp: paragraph --><p>{text}</p><!--/wp:paragraph -->'
    return paragraph


def bold_paragraph(text_to_bold):
    """
    bold paragraph function for wp
    :param text_to_bold:
    :return: strong paragraph
    """
    strong_paragraph = f'<!-- wp:paragraph --><p><strong>{text_to_bold}</strong></p><!-- /wp:paragraph -->'
    return strong_paragraph


def wp_list(list_items):
    """
    list function for wp
    :param list_items:
    :return: list
    """
    first_part = '<!-- wp:list --> <ul>'
    last_part = '</ul><!-- /wp:list -->'
    for item in list_items:
        list_item = f'<!-- wp:list-item --><li>{item}</li><!-- /wp:list-item -->'
        first_part += list_item
    list_code = first_part + last_part
    return list_code


intro_data = buyer_guide(f'write down an introduction about {keyword}')
main_data1 = buyer_guide(f'write 5 points about why should you choose a {keyword}')

number_list1 = ['1. ', '2. ', '3. ', '4. ', '5. ']
for number in number_list1:
    main_data1 = main_data1.replace(number, '')

main_data1_f = main_data1.split('\n')

while '' in main_data1_f:
    main_data1_f.remove('')

main_data2 = buyer_guide(f'write 300 words about what to look for when choosing {keyword}')
main_data_qa = buyer_guide(f'Write down 5 questions what we should know when we are purchasing {keyword}')
questions_answers = ques_answer(main_data_qa)
conclusion = buyer_guide(f'write down 150 words conclusion about {keyword}')

# print(intro_data+main_data1+main_data2)
# print(questions_answers)
# print(conclusion)

# print(h3_heading(keyword))

buyer_guide_h2 = h2_heading('Buyer Guide: What to Look When Buying ' + keyword)
buyer_guide_intro = paragraph(intro_data)
buyer_guide_h3 = h3_heading('Why Should You Choose ' + keyword)
buyer_guide_data1 = wp_list(main_data1_f)
buyer_guide_h3_another = h3_heading('What to Look for When Choosing ' + keyword)
buyer_guide_data2 = paragraph(main_data2)

faq = h2_heading('Frequently Asked Questions Related to ' + keyword)
faq_content = ''
for key, values in questions_answers.items():
    faq_content_question = bold_paragraph(key)
    faq_content_answer = paragraph(values)
    faq_content = faq_content + faq_content_question + faq_content_answer

conclusion_h2 = h2_heading('Conclusion')
conclusion_wp = paragraph(conclusion)

buyer_guide_content = buyer_guide_h2.strip('\n') + buyer_guide_intro.strip('\n') \
                      + buyer_guide_h3.strip('\n') + buyer_guide_data1.strip('\n') \
                      + buyer_guide_h3_another.strip('\n') + buyer_guide_data2.strip('\n') + faq.strip('\n') \
                      + faq_content.strip('\n') + conclusion_h2.strip('\n') + conclusion_wp.strip('\n')


create_wp_post(api_url, title, buyer_guide_content, slug)
