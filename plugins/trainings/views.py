from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Sum, Count

from base.http import Http403
from site_settings.utils import get_setting
from trainings.models import Training, Completion
from trainings.forms import CompletionForm
from perms.utils import get_notice_recipients, has_perm, get_query_filters, has_view_perm
from event_logs.models import EventLog

from perms.utils import update_perms_and_save

try:
    from notification import models as notification
except:
    notification = None

def detail(request, pk=None, template_name="trainings/detail.html"):
    if not pk: return HttpResponseRedirect(reverse('trainings.search'))
    
    training = get_object_or_404(Training, pk=pk)

    if request.user.is_authenticated():
    
        if has_perm(request.user, 'trainings.view_completion'):
            completions = Completion.objects.filter(training=training)
        else:
            completions = Completion.objects.filter(training=training, owner=request.user)
        completions = completions.order_by('finish_dt')

        try:
            user_completion = Completion.objects.get(training=training, owner=request.user)
        except:
            user_completion = None
        
        if has_view_perm(request.user, 'trainings.view_training', training):
            log_defaults = {
                'event_id' : 1011500,
                'event_data': '%s (%d) viewed by %s' % (training._meta.object_name, training.pk, request.user),
                'description': '%s viewed' % training._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': training,
            }
            EventLog.objects.log(**log_defaults)
            return render_to_response(template_name, {'training': training, 'completions':completions,'user_completion':user_completion}, 
                context_instance=RequestContext(request))
        else:
            raise Http403
    else:
        raise Http403

def search(request, template_name='trainings/search.html'):
    """
    This page lists out all trainings from newest to oldest.
    If a search index is available, this page will also
    have the option to search through trainings.
    """
    has_index = get_setting('site', 'global', 'searchindex')
    query = request.GET.get('q', None)

    if has_index and query:
        trainings = Training.objects.search(query, user=request.user)
        trainings = trainings.order_by('-create_dt')
    else:
        if has_perm(request.user, 'trainings.view_training') and has_perm(request.user, 'trainings.view_completion'):
            trainings = Training.objects.all().annotate(completions=Count('completion')).order_by('-completions')
        else:
            filters = get_query_filters(request.user, 'trainings.view_training')
            trainings = Training.objects.filter(filters).distinct()
            if request.user.is_authenticated():
                trainings = trainings.select_related()
            trainings = trainings.order_by('-create_dt')

    EventLog.objects.log(**{
        'event_id' : 1011400,
        'event_data': '%s searched by %s' % ('Training', request.user),
        'description': '%s searched' % 'Training',
        'user': request.user,
        'request': request,
        'source': 'trainings'
    })
    
    return render_to_response(template_name, {'trainings':trainings}, 
        context_instance=RequestContext(request))

def search_redirect(request):
    return HttpResponseRedirect(reverse('trainings'))

@login_required
def completion_add(request, training_pk=None, form_class=CompletionForm, template_name="trainings/completion-add.html"):

    training = get_object_or_404(Training, pk=training_pk)

    # check permission
    if not has_perm(request.user,'trainings.add_completion'):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, user=request.user)
        if form.is_valid():
            completion = form.save(commit=False)
            completion.training = training

            # update all permissions and save the model
            completion = update_perms_and_save(request, form, completion)

            log_defaults = {
                'event_id' : 1011150,
                'event_data': '%s (%d) added by %s' % (completion._meta.object_name, completion.pk, request.user),
                'description': '%s added' % completion._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': completion,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.SUCCESS, 'Successfully completed %s' % training)

            return HttpResponseRedirect(reverse('trainings.detail', args=[training.pk]))
    else:
        form = form_class(user=request.user)
       
    return render_to_response(template_name, {'form':form, 'training':training}, 
        context_instance=RequestContext(request))

@login_required
def completion_edit(request, completion_pk=None, form_class=CompletionForm, template_name="trainings/completion-edit.html"):

    completion = get_object_or_404(Completion, pk=completion_pk)
    training = completion.training

    # check permission
    if not has_perm(request.user,'trainings.change_completion'):
        raise Http403

    if request.method == "POST":
        form = form_class(request.POST, instance=completion, user=request.user)
        if form.is_valid():
            completion = form.save(commit=False)

            # update all permissions and save the model
            completion = update_perms_and_save(request, form, completion)

            log_defaults = {
                'event_id' : 1011250,
                'event_data': '%s (%d) added by %s' % (completion._meta.object_name, completion.pk, request.user),
                'description': '%s added' % completion._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': completion,
            }
            EventLog.objects.log(**log_defaults)
            
            messages.add_message(request, messages.SUCCESS, 'Successfully edited completion for %s' % training)

            return HttpResponseRedirect(reverse('trainings.detail', args=[training.pk]))
    else:
        form = form_class(instance=completion, user=request.user)
       
    return render_to_response(template_name, {'form':form, 'training':training, 'completion':completion}, 
        context_instance=RequestContext(request))

@login_required
def completion_delete(request, completion_pk=None, template_name="trainings/completion-delete.html"):
    completion = get_object_or_404(Completion, pk=completion_pk)
    training = completion.training

    if has_perm(request.user,'trainings.delete_completion'):
        if request.method == "POST":
            log_defaults = {
                'event_id' : 1011350,
                'event_data': '%s (%d) deleted by %s' % (completion._meta.object_name, completion.pk, request.user),
                'description': '%s deleted' % completion._meta.object_name,
                'user': request.user,
                'request': request,
                'instance': completion,
            }
            
            EventLog.objects.log(**log_defaults)

            messages.add_message(request, messages.SUCCESS, 'Successfully deleted completion for %s' % training)

            completion.delete()
                                    
            return HttpResponseRedirect(reverse('trainings.detail', args=[training.pk]))
    
        return render_to_response(template_name, {'training':training, 'completion':completion}, 
        context_instance=RequestContext(request))
    else:
        raise Http403

@login_required
def completion_report_all(request, template_name="trainings/report-all.html"):
    start_dt = datetime.now()-timedelta(days=90)
    if 'start_dt' in request.GET.keys():
        start_dt = request.GET['start_dt']

    end_dt = datetime.now()
    if 'end_dt' in request.GET.keys():
        end_dt = request.GET['end_dt']
    
    if has_perm(request.user,'trainings.view_completion'):
        completions = Completion.objects.values('owner', 'owner__last_name','owner__first_name').filter(finish_dt__gte=start_dt, finish_dt__lte=end_dt).annotate(points_sum=Sum('training__points')).order_by('-points_sum')
    
        all_user_completions = []
        for user in completions:
            user_completions = Completion.objects.filter(finish_dt__gte=start_dt, finish_dt__lte=end_dt,owner=user['owner']).order_by('-finish_dt')
            all_user_completions.append({'user':user['owner'], 'completions':user_completions})
    
        return render_to_response(template_name, locals(), 
        context_instance=RequestContext(request))
    else:
        Http403
