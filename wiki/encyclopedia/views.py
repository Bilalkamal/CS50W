
import re, random
from unittest import result

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from  markdown2 import Markdown
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })
    
def entry(request, title):
    if not util.get_entry(title.capitalize()):
        return render(request, "encyclopedia/error.html", {
            "error": f"'{title}' not found!"
        })
    html = Markdown().convert(util.get_entry(title))
    return render(request, "encyclopedia/entry.html", {
        "entry": html,
        "title": title
    })


def search(request):
    value = request.GET.get("q",'')
    if value == "":
        return HttpResponseRedirect(reverse("index"))
    if (util.get_entry(value.capitalize())):
        return HttpResponseRedirect(reverse("entry", args=[value]))

    results = [
        entry
        for entry in util.list_entries()
        if re.search(value, entry, re.IGNORECASE)
    ]

    return render(request, "encyclopedia/search.html", {
        "results": results,
        "search": len(results)>0,
        "value": value
        })
        
def create(request):
    if request.method == "POST":
        title = request.POST.get("name", "").capitalize()
        content = request.POST.get("entry", "")
        if util.get_entry(title):
            return render(request, "encyclopedia/error.html", {
                "error": f"'{title}' already exists!"
            })
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "encyclopedia/create.html") 

def edit(request, title):
    if not util.get_entry(title):
        return render(request, "encyclopedia/error.html", {
            "error": f"'{title}' not found!"
        })
    if request.method == "POST" and request.POST.get("entry", ""):
        util.save_entry(title, request.POST.get("entry", ""))
        return HttpResponseRedirect(reverse("index"))

    md = util.get_entry(title)
    return render(request, "encyclopedia/edit.html", {
        "entry": md,
        "title": title
    }) 
    
    
def random_page(request):
    entries = util.list_entries()
    return entry(request, random.choice(entries))