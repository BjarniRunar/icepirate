from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from group.models import Group
from member.models import Member
from member.forms import MemberForm

from member import kennitala

from icepirate.saml import authenticate

@login_required
def list(request, group_techname):

    if group_techname:
        members = Member.objects.filter(groups__techname=group_techname)
    else:
        members = Member.objects.all()

    groups = Group.objects.all()

    context = {
        'members': members,
        'groups': groups,
        'group_techname': group_techname,
    }
    return render_to_response('member/list.html', context)

@login_required
def add(request):

    if request.method == 'POST':
        form = MemberForm(request.POST)

        if form.is_valid():
            member = form.save()
            return HttpResponseRedirect('/member/view/%s' % member.kennitala)

    else:
        form = MemberForm()

    return render_to_response('member/add.html', { 'form': form }, context_instance=RequestContext(request))

@login_required
def edit(request, kennitala):

    member = get_object_or_404(Member, kennitala=kennitala)

    if request.method == 'POST':
        member.groups = request.POST.getlist('groups')
        form = MemberForm(request.POST, instance=member)

        if form.is_valid():
            member = form.save()
            return HttpResponseRedirect('/member/view/%s/' % kennitala)

    else:
        form = MemberForm(instance=member)

    return render_to_response('member/edit.html', { 'form': form, 'member': member }, context_instance=RequestContext(request))

@login_required
def delete(request, kennitala):

    member = get_object_or_404(Member, kennitala=kennitala)

    if request.method == 'POST':
        member.delete()
        return HttpResponseRedirect('/member/list/')

    return render_to_response('member/delete.html', { 'member': member }, context_instance=RequestContext(request))

@login_required
def view(request, kennitala):

    member = get_object_or_404(Member, kennitala=kennitala)

    return render_to_response('member/view.html', { 'member': member }, context_instance=RequestContext(request))

def verify(request):

    member = None

    kennitala = request.session.get('kennitala', None)
    if kennitala:
        member = Member.objects.get(kennitala=kennitala)

    if member is None:
        auth = authenticate(request, settings.AUTH_URL)
        try:
            member = Member.objects.get(kennitala=auth['kennitala'])
            member.verified = True
            member.auth_token = request.GET['token']
            member.auth_timing = datetime.now()
            member.save()

            request.session['kennitala'] = member.kennitala
            return redirect('/member/verify/')
        except:
            pass

    return render_to_response('member/verify.html', { 'member': member, }, context_instance=RequestContext(request))

