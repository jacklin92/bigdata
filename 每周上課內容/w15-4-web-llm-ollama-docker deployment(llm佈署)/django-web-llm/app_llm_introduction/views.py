from django.shortcuts import render
import markdown



def model_introduction(request):
    # Read the markdown file
    markdown_file_path = 'app_llm_introduction/docs/model-introduction.md'
    # Read the markdown file
    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['fenced_code', 'codehilite'])
    
    # Pass the HTML content to the template
    context = {
        'model_intro_html_content': html_content
    }

    return render(request, "app_llm_introduction/model-introduction.html", context)

