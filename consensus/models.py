from __future__ import unicode_literals

from django.db import models
# Create your models here.


class User(models.Model):
    '''
    Holds users name/password
    '''
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Discussion(models.Model):
    '''
    Class containing data on discussions
    '''
    ncomments = models.IntegerField(default=0, null=True)


class Submission(models.Model):
    '''
    Super class for other model classes
    '''
    text = models.CharField(max_length=2000, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, null=True)
    rank = models.FloatField(default=0.5)
    num_up = models.IntegerField(default=0)
    num_dw = models.IntegerField(default=0)
    num_xx = models.IntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['-rank', 'id']

    def get_text(self):
        return self.text

    def __str__(self):
        return self.text


class Comment(Submission):
    '''
    Class containing timing of discussion
    '''


class Project(Submission):
    '''
    Project class (for holding generals and under)
    '''


class General(Submission):
    '''
    Contains own text, author, rank, a list of member specifics (through generalspecific) and a list of voters (through generalvote)
    '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="gproject", null=True)
    votes = models.ManyToManyField(User, through='GeneralVote', through_fields=('general', 'user'), related_name='gvotes')

    def save(self, *args, **kwargs):
        '''
        Create discussion on save if one doesn't exist
        :param args:
        :param kwargs:
        :return:
        '''
        if not self.discussion:
            self.discussion = Discussion.objects.create()
        super(General, self).save(*args, **kwargs)

    def get_majority_specific_text(self):
        '''
        Return current majority specific for general
        :return:
        '''
        if self.specific_set.all():
            return self.specific_set.order_by('-rank')[0].get_text()

    def get_all_text(self):
        '''
        Retursn general's own text and a list of facet text from the majority specific
        :return:
        '''
        return self.text, self.get_majority_specific_text()


class Facet(Submission):
    '''
    Contains own text, author, and the general to which it belongs
    '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="fproject", null=True)
    general = models.ForeignKey(General, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if not self.discussion:
            self.discussion = Discussion.objects.create()
        super(Facet, self).save(*args, **kwargs)


class Specific(Submission):
    '''
    Contains own general and author, votes (through specific votes) and member facets (through specificfacet)
    '''
    general = models.ForeignKey(General, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="sproject", null=True)
    # Link specifics to votes
    votes = models.ManyToManyField(User, through='SpecificVote', through_fields=('specific', 'user'), related_name='svotes' )

    # Link facets to specific
    facets = models.ManyToManyField(Facet, through="SpecificFacet", through_fields=('specific', 'facet',))

    def get_text(self):
        fset = self.facets.all()
        rlist = list()
        for f in fset:
            rlist.append(f.text)
        return rlist

    def __str__(self):
        return self.get_text()

    def save(self, *args, **kwargs):
        if not self.discussion:
            self.discussion = Discussion.objects.create()
        super(Specific, self).save(*args, **kwargs)


class Bundle(Submission):
    '''
    Create a general bundle class, contains creator, project, and vo
    '''
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bproject')
    generals = models.ManyToManyField(General, through="BundleGeneral", through_fields=('bundle', 'general', ))
    votes = models.ManyToManyField(User, through="BundleVote", through_fields=('bundle', 'user', ), related_name='bvotes')
    discussion = None

    def get_all_text(self):
        '''
        Returns a list of tuples, each containing (general text, facet text list) for every general in the bundle
        :return:
        '''
        gset = self.generals.all()
        rlist = list()
        for g in gset:
            rlist.append(g.get_all_text())
        return rlist

    def get_text(self):
        gset = self.generals.all()
        rlist = list()
        for g in gset:
            rlist.append(g.text)
        return rlist

    def __str__(self):
        return self.get_text()

    def save(self, *args, **kwargs):
        if not self.discussion:
            self.discussion = Discussion.objects.create()
        super(Bundle, self).save(*args, **kwargs)


class Vote(models.Model):
    '''
    Super class of vote objects
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    timestamp = models.DateTimeField(auto_now=True, null=True)
    UP = "up"
    DW = "dw"
    XX = "xx"
    CHOICES = (
        (UP, 'up'),
        (DW, 'dw'),
        (XX, 'xx'),
    )
    choice = models.CharField(max_length=2, choices=CHOICES, default=XX)

    class Meta:
        abstract = True


class BundleVote(Vote):
    '''
    Linking class between general bundles and votes
    '''
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name + ' ' + self.bundle.text


class GeneralVote(Vote):
    '''
    Linking class between generals and voters (contains direction of each vote)
    '''
    general = models.ForeignKey(General, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name + ' ' + self.general.text


class SpecificVote(Vote):
    '''
    Linking class between a specific and a voter (contains direction of vote)
    '''
    specific = models.ForeignKey(Specific, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name + ' ' + self.specific.get_text()


class FacetVote(Vote):
    '''
    Linking class between a specific and a voter (contains direction of vote)
    '''
    Facet = models.ForeignKey(Facet, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name + ' ' + self.Facet.text


class BundleGeneral(models.Model):
    '''
    Linking class between bundles and generals
    '''
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE)
    general = models.ForeignKey(General, on_delete=models.CASCADE)


class SpecificFacet(models.Model):
    '''
    Linking class between a specific and a facet
    '''
    specific = models.ForeignKey(Specific, on_delete=models.CASCADE)
    facet = models.ForeignKey(Facet, on_delete=models.CASCADE)


class GeneralFacet(models.Model):
    '''
    Linking class between a specific and a facet
    '''
    general = models.ForeignKey(General, on_delete=models.CASCADE)
    facet = models.ForeignKey(Facet, on_delete=models.CASCADE)


class DiscussionComment(models.Model):
    '''
    Linking class between a discussion and its comments
    '''
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)



