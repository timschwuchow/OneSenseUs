from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from .models import Specific, General, User, GeneralVote, SpecificVote, Facet, SpecificFacet, \
    GeneralFacet, Project, Bundle, BundleGeneral, BundleVote, Discussion, Comment
from .forms import FacetSelectionForm, GeneralSelectionForm

UP = "up"
DW = "dw"
XX = "xx"


def update_general_ranks(pid):
    '''
    Recompute general rankings
    :return:
    '''
    p = Project.objects.get(pk=int(pid))
    glist = General.objects.filter(project=p)
    for g in glist:
        gvset = g.generalvote_set.all()
        g.num_up = gvset.filter(choice=UP).count()
        g.num_dw = gvset.filter(choice=DW).count()
        g.num_xx = gvset.filter(choice=XX).count()
        g.rank = (g.num_up + 0.5 * g.num_xx)/(g.num_up + g.num_dw + g.num_xx)
        g.save()
    return True


def update_bundle_ranks(pid):
    '''
    Recompute general rankings
    :return:
    '''
    p = Project.objects.get(pk=int(pid))
    blist = Bundle.objects.filter(project=p)
    for b in blist:
        bvset = b.bundlevote_set.all()
        b.num_up = bvset.filter(choice=UP).count()
        b.num_dw = bvset.filter(choice=DW).count()
        b.num_xx = bvset.filter(choice=XX).count()
        b.rank = (b.num_up + 0.5 * b.num_xx)/(b.num_up + b.num_dw + b.num_xx)
        b.save()
    return True


def update_specific_ranks(gid):
    '''
    Update ranks of specifics for general gid
    :param gid:
    :return:
    '''
    g = General.objects.get(pk=int(gid))
    slist = g.specific_set.all()
    for s in slist:
        svset = s.specificvote_set.all()
        s.num_up = svset.filter(choice=UP).count()
        s.num_dw = svset.filter(choice=DW).count()
        s.num_xx = svset.filter(choice=XX).count()
        s.rank = (s.num_up + 0.5 * s.num_xx)/(s.num_up + s.num_dw + s.num_xx)
        s.save()
    return True


def update_all_ranks(pid):
    '''
    Updates general ranks and each specific rank
    :return:
    '''
    p = Project.objects.get(pk=int(pid))
    glist = General.objects.filter(project=p)
    update_general_ranks(pid)
    update_bundle_ranks(pid)
    for g in glist:
        update_specific_ranks(g.id)
    return True


def create_project(request, uid):
    '''
    Create new project
    :param request:
    :param uid:
    :return:
    '''
    project_name = request.POST['project_name']
    u = User.objects.get(pk=int(uid))
    p = Project(text=project_name, author=u)
    p.save()
    return HttpResponseRedirect(reverse('projectlist', args=(uid, )))


def create_general(request, uid, pid):
    '''
    Create new general within project
    :param request:
    :param uid:
    :param pid:
    :return:
    '''
    u = User.objects.get(pk=int(uid))
    p = Project.objects.get(pk=int(pid))
    try:
        input_text = request.POST['text']
    except:
        pass
    else:
        # Create general
        g = General(text=input_text, author=u, project=p)
        g.save()
        # Create generalvote objects for each user
        for u in User.objects.all():
            gv = GeneralVote(general=g, user=u)
            gv.save()

    return HttpResponseRedirect(reverse('generallist', args=(uid, pid)))


def create_specific(request, uid, pid, gid):
    '''
    Extract information from form to create new specific
    :param request:
    :param uid:
    :param gid:
    :return:
    '''
    u = User.objects.get(pk=int(uid))
    g = General.objects.get(pk=int(gid))
    p = Project.objects.get(pk=int(pid))
    form = FacetSelectionForm(request.POST)
    s = Specific(general=g, author=u, project=p)
    s.save()

    # Link facets to new specific
    if form.is_valid():
        fselection = form.cleaned_data.get('facets')
        for f in fselection:
            SpecificFacet.objects.get_or_create(specific=s, facet=f)

    # Update specific with text of facets
    s.text = s.get_text()
    s.save()

    # Create all specific-vote objects for new specific
    for u in User.objects.all():
        SpecificVote.objects.get_or_create(user=u, specific=s)

    return HttpResponseRedirect(reverse('general', args=(uid, pid, gid,)))


def create_general_bundle(request, uid, pid):
    u = User.objects.get(pk=int(uid))
    p = Project.objects.get(pk=int(pid))
    bundle = Bundle(author=u, project=p)
    form = GeneralSelectionForm(request.POST)
    if form.is_valid():
        bundle.save()
        gselection = form.cleaned_data.get('generals')
        for g in gselection:
            gi = BundleGeneral(bundle=bundle, general=g)
            gi.save()
        for uu in User.objects.all():
            BundleVote.objects.get_or_create(bundle=bundle, user=uu)
        bundle.text = bundle.get_text()
        bundle.save()
        return HttpResponseRedirect(reverse('generalbundlelist', args=(uid, pid,)))
    else:
        return HttpResponseRedirect(reverse('generalbundleconstructor', args=(uid, pid,)))


def front_page_view(request):
    return render(request, 'consensus/login.html', context={})


def bundle_vote_view(request, uid, pid, bid):
    '''
    Vote on bundles
    :param request:
    :param uid:
    :param pid:
    :param bid:
    :return:
    '''
    voted_up = (request.POST['vote'] == "Up")
    u = User.objects.get(id=int(uid))
    p = Project.objects.get(pk=int(pid))
    b = Bundle.objects.get(id=int(bid))
    bv = BundleVote.objects.get_or_create(user=u, bundle=b)
    # Modify general vote object with new vote (up or down)
    if voted_up and bv.choice == UP:
        bv.choice = XX
    elif voted_up:
        bv.choice = UP
    elif not voted_up and bv.choice == DW:
        bv.choice = XX
    else:
        bv.choice = DW
    bv.save()
    return HttpResponseRedirect(reverse('generalbundlelist', args=(uid, pid)))


def general_bundle_list_view(request, uid, pid):
    '''
    View general bundle list for project
    :param request:
    :param uid: user id
    :param pid: project id
    :return:
    '''
    u = User.objects.get(pk=int(uid))
    p = Project.objects.get(pk=int(pid))
    votes = BundleVote.objects.filter(user=u)
    update_bundle_ranks(pid)
    blist = Bundle.objects.filter(project=p)

    uvl = list()
    for b in blist:
        if not b.text:
            b.text = b.get_text()
        uvl.append((b, votes.get(bundle=b), ))
    context = {'u': u, 'p': p, 'uvl': uvl}
    return render(request, 'consensus/generalbundlelist.html', context)


def try_login_view(request):
    name = request.POST['name']
    password = request.POST['password']

    try:
        u = User.objects.get(name=name)
    except:
        return render(request, 'consensus/loginerror.html', context={})
    else:
        if u.password == password:
            return HttpResponseRedirect(reverse('projectlist', args=(u.id,)))
        else:
            return render(request, 'consensus/loginerror.html', context={})


def project_list_view(request, uid):
    '''
    View of overall project list
    :param request:
    :param uid:
    :return:
    '''
    u = User.objects.get(pk=int(uid))
    plist = Project.objects.all()
    context = {'u': u, 'plist': plist}
    return render(request, 'consensus/projectlist.html', context)


def general_list_view(request, uid, pid):
    '''
    Main view of general ranks for user uid
    :param request:
    :param uid: user id
    :param pid: project id
    :return:
    '''
    u = User.objects.get(id=int(uid))
    p = Project.objects.get(pk=int(pid))
    glist = General.objects.filter(project=p)

    # Create generalvote objects for user if missing
    for g in glist:
        GeneralVote.objects.get_or_create(user=u, general=g)

    # Update vote tallies and resort
    update_general_ranks(pid)
    glist = General.objects.filter(project=p).order_by('-rank')

    # Get current user choices and pass as a list of vote choices
    gvotes = GeneralVote.objects.filter(user=u)

    # Reorder user votes to match general vote ordering
    uvl = list()
    for g in glist:
        uvl.append((g, gvotes.get(general=g), ))

    # Build page
    context = {'uvl' : uvl, 'glist': glist, 'u' : u, 'p' : p}
    return render(request, 'consensus/generallist.html', context=context)


def signup_view(request):
    return render(request,'consensus/signup.html', context={})


def try_signup_view(request):

    name = request.POST['name']
    password = request.POST['password']
    # Check proposed user name against existing, otherwise create user
    ulist = [u.name for u in User.objects.all()]
    if any(name in u for u in ulist):
        context = {'tryagain': True }
        return render(request, 'consensus/signup.html', context=context)
    else:
        u = User(name=name, password=password)
        u.save()
        return render(request, 'consensus/login.html', context={})


def general_view(request, uid, pid, gid):
    g = General.objects.get(pk=int(gid))
    p = Project.objects.get(pk=int(pid))
    u = User.objects.get(pk=int(uid))

    # Sort specific list
    specific_list = Specific.objects.filter(general=g).order_by('-rank')

    # Get current user choices for specifics within the general
    svotes = SpecificVote.objects.filter(user=u, specific__general=g)

    # Reorder user votes to match general vote ordering
    uvl = list()
    for s in specific_list:
        uvl.append((s, svotes.get(specific=s), ))

    context = {'g': g, 'uvl': uvl, 'u' : u, 'p' : p}
    return render(request, 'consensus/general.html', context)


def general_vote_view(request, uid, pid, gid):
    voted_up = (request.POST['vote'] == "Up")
    u = User.objects.get(id=int(uid))
    p = Project.objects.get(pk=int(pid))
    g = General.objects.get(id=int(gid))
    gv = GeneralVote.objects.get(user=u, general=g)
    # Modify general vote object with new vote (up or down)
    if voted_up and gv.choice == UP:
        gv.choice = XX
    elif voted_up:
        gv.choice = UP
    elif not voted_up and gv.choice == DW:
        gv.choice = XX
    else:
        gv.choice = DW
    gv.save()
    return HttpResponseRedirect(reverse('generallist', args=(uid, pid)))


def specific_vote_view(request, uid, pid, gid, sid):
    '''
    Modify specificvote with new choice of user
    :param request:
    :param uid:
    :param gid:
    :param sid:
    :return:
    '''
    voted_up = (request.POST['vote'] == "Up")
    u = User.objects.get(id=int(uid))
    p = Project.objects.get(pk=int(pid))
    s = Specific.objects.get(id=int(sid))
    sv = SpecificVote.objects.get(user=u, specific=s)
    # Modify specific vote object with new choice
    if voted_up and sv.choice == UP:
        sv.choice = XX
    elif voted_up:
        sv.choice = UP
    elif not voted_up and sv.choice == DW:
        sv.choice = XX
    else:
        sv.choice = DW
    sv.save()
    update_specific_ranks(gid)
    return HttpResponseRedirect(reverse('general', args=(uid, pid, gid,)))


def general_constructor_view(request, uid, pid):
    '''
    Returns general constructor form
    :param request:
    :param uid:
    :return:
    '''
    u = User.objects.get(id=int(uid))
    p = Project.objects.get(pk=int(pid))
    context = {'u': u, 'p': p}
    return render(request, 'consensus/genconstructor.html', context)


def project_constructor_view(request, uid):
    '''
    serve project constructor page
    :param request:
    :param uid:
    :return:
    '''
    u = User.objects.get(pk=int(uid))
    context = {'u' : u}
    return render(request, 'consensus/projectconstructor.html', context)


def facets_view(request, uid, pid, gid):
    '''
    View list of facets for gid
    :param request:
    :param uid:
    :param gid:
    :return:
    '''
    u = User.objects.get(pk=int(uid))
    p = Project.objects.get(pk=int(pid))
    g = General.objects.get(pk=int(gid))
    flist = g.facets.all()
    context = {'flist': flist, 'u': u, 'g': g, 'p': p}
    return render(request, 'consensus/facets.html', context)


def create_facet(request, uid, pid, gid):
    '''
    Create new facet and return to facet page
    :param request:
    :param uid: user id
    :param pid: project id
    :param gid: general id
    :return:
    '''
    u = User.objects.get(pk=int(uid))
    p = Project.objects.get(pk=int(pid))
    g = General.objects.get(pk=int(gid))
    f = Facet(author=u, text=request.POST['text'], project=p, general=g)
    f.save()
    gf = GeneralFacet(general=g, facet=f)
    gf.save()
    return HttpResponseRedirect(reverse('facetsview', args=(uid, pid, gid,)))


def facet_constructor_view(request, uid, pid, gid):
    '''
    Returns form to propose facet to user for project/genral
    :param request:
    :param uid: user id
    :param pid: project id
    :param gid: general id
    :return:
    '''
    u = User.objects.get(pk=int(uid))
    g = General.objects.get(pk=int(gid))
    p = Project.objects.get(pk=int(pid))
    context = {'g': g, 'u': u, 'p': p}
    return render(request, 'consensus/facetconstructor.html', context)


def specific_constructor_view(request, uid, pid, gid):
    '''
    Create forms for constructing specific2 object
    :param request:
    :param uid: user
    :param pid: project
    :param gid: general
    :return:
    '''
    u = User.objects.get(pk=int(uid))
    g = General.objects.get(pk=int(gid))
    p = Project.objects.get(pk=int(pid))
    f = FacetSelectionForm(gid=int(gid))
    context = {'u': u, 'g': g, 'f': f, 'p': p}
    return render(request, 'consensus/specconstructor.html', context)


def general_bundle_constructor_view(request, uid, pid):
    '''
    Create form and page for constructing bundles of generals
    :param request:
    :param uid:
    :param pid:
    :return:
    '''
    u = User.objects.get(pk=int(uid))
    p = Project.objects.get(pk=int(pid))
    form = GeneralSelectionForm(pid=p.id)
    context = {'u': u, 'p': p, 'form': form}
    return render(request, 'consensus/generalbundleconstructor.html', context)


def discussion_view(request, uid, did):
    '''
    Returns view of discussion
    :param request:
    :param uid:
    :param did:
    :return:
    '''
    user = User.objects.get(pk=int(uid))
    discussion = Discussion.objects.get(pk=int(did))
    # Get discussion parent
    if discussion.general_set.all():
        parent = discussion.general_set.all()[0]
    elif discussion.project_set.all():
        parent = discussion.project_set.all()[0]
    elif discussion.facet_set.all():
        parent = discussion.facet_set.all()[0]
    elif discussion.bundle_set.all():
        parent = discussion.bundle_set.all()[0]
    elif discussion.specific_set.all():
        parent = discussion.specific_set.all()[0]
    comment_list = discussion.comment_set.all()
    context = {'user' : user, 'discussion' : discussion, 'comment_list' : comment_list, 'parent': parent}
    return render(request, 'consensus/discussion.html', context)


def submit_comment(request, uid, did):
    '''
    Submit comment
    :param request:
    :param uid:
    :param did:
    :return:
    '''
    user = User.objects.get(pk=int(uid))
    discussion = Discussion.objects.get(pk=int(did))
    comment_input = request.POST['comment_input']
    comment = Comment(discussion=discussion, author=user, text=comment_input)
    comment.save()
    return HttpResponseRedirect(reverse('discussion', args=(uid, did, )))