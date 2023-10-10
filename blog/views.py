# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
'''
    Class-based views
'''
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'    
    
    
'''
    Function-based views
'''
# def post_list(request):
#     object_list = Post.published.all()
#     paginator = Paginator(object_list, 3)
#     page = request.GET.get('page')
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     return render(
#         request, 
#         'blog/post/list.html',
#         {   'page': page,
#             'posts': posts}
#     )

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post, 
        slug=post, 
        status='published', 
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    comments = post.comments.filter(active=True)
    
    if request.method =='POST':
        # For posted comment
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(
        request,
        'blog/post/detail.html',
        {'post':post,
         'comments': comments,
         'comment_form': comment_form}
    )
    
'''
    To handle forms
'''

def post_share(request, post_id):
    post = get_object_or_404(Post, id = post_id, status= 'published')
    sent = False
    
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        
        if form.is_valid():
            clean_dataform = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject ='{} ({}) recommends you reading "{}"'.format(clean_dataform['name'], 
                                                                  clean_dataform['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title,
                                                                     post_url,
                                                                     clean_dataform['name'],
                                                                     clean_dataform['comments'])
            send_mail(subject, message, 'deepak.191708@ncit.edu.np', [clean_dataform['to']])
            sent = True
    else:
        form = EmailPostForm() 
        return render(request, 'blog/post/share.html',{'post': post,
                                                       'form': form,
                                                       'sent': sent})