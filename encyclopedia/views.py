from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown2
import random
from . import util


class WikiNewForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 
                                                          'placeholder' : 'Enter title'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 
                                                           'placeholder' : '# Enter markdown'}))


# Home page with list of encyclopedia titles
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


# Display encyclopedia entry page
def entry_page(request, name):
    if util.get_entry(name) != None:
        # Convert the entry content to Markdown
        content = markdown2.markdown(util.get_entry(name))
        return render(request, "encyclopedia/entry_page.html", {
            "title": name,
            "content": content
        })
    else: 
        # If an encyclopedia title does not exist, return error page
        return render(request, "encyclopedia/error.html", {
            "encyclopedia": util.get_entry(name) == None
        })

    
    # if util.get_entry(name) == None:
    #     return render(request, "encyclopedia/error.html", {
    #         "encyclopedia": util.get_entry(name) == None
    #     })
    # else:
        
    #     content = markdown2.markdown(util.get_entry(name))
    #     return render(request, "encyclopedia/entry_page.html", {
    #         "title": name,
    #         "content": content
    #     })



# Search encyclopedia
def search(request):

    # Check if method is GET
    if request.method == "GET":

        # Take the input data
        query = request.GET['q']

        entries = util.list_entries()
        # If the search query match, return the encyclopedia page
        if query.lower() in [x.lower() for x in entries]:
            return entry_page(request, query)

        # Display all encyclopedia entries that have the search query as a substring
        results = [entry for entry in entries if query.lower() in entry.lower()]
        return render(request, "encyclopedia/search.html", {
            "entries": results,
        })
    else:
        return render(request, "encyclopedia/index.html")



# Create new encyclopedia entry
def new_page(request):
    # Check if method is POST
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = WikiNewForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            # Isolate the inputs from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # If an encyclopedia entry already exists return error page.
            entries = util.list_entries()
            if title in entries:
                return render(request, "encyclopedia/error.html")
            
            # Add and create new file to the entries
            util.save_entry(title, content.replace("\n", ""))

            # Redirect user to the entry page
            return entry_page(request, title)

        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/new_page.html", {
                "form": form
            })

    return render(request, "encyclopedia/new_page.html", {
        "form": WikiNewForm()
    })



# Edit encyclopedia
def edit(request, title):
    entry = util.get_entry(title)
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = WikiNewForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            # Isolate the inputs from the 'cleaned' version of form data
            edit_title = request.POST['title']
            edit_content = request.POST['content']

            # Save the new title and content to the entries
            util.save_entry(edit_title, edit_content.replace("\n", ""))

            # Redirect user to the entry page
            return entry_page(request, edit_title)

        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/edit.html", {
                "form": form
            })
    
    # Pre-populated with the existing Markdown content of the page
    content_data = {'title': title, 'content': entry}

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": WikiNewForm(content_data)
    })



# Return a random encyclopedia entry page
def random_page(request):
    titles = util.list_entries()
    title = random.choice(titles)
    return entry_page(request, title)