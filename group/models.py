from django.db import models
from datetime import datetime

from locationcode.models import LocationCode


class Group(models.Model):
    COMBINATION_METHODS = (('union', 'Union'),
                           ('intersection', 'Intersection'))

    name = models.CharField(max_length=50, unique=True)
    techname = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    added = models.DateTimeField(default=datetime.now)

    auto_subgroups = models.ManyToManyField('Group', related_name='auto_parent_groups')
    auto_locations = models.ManyToManyField(LocationCode, related_name='auto_location_groups')
    combination_method = models.CharField(max_length=30,
                                          verbose_name="Combination method",
                                          choices=COMBINATION_METHODS,
                                          default=COMBINATION_METHODS[0][0])


    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_members(self, subgroups=True, locations=True):
        from member.models import Member

        group_ids = set([self.id])
        if subgroups:
            group_ids |= set(self.auto_subgroups.values_list('id', flat=True))
        mQs = models.Q(groups__id__in = group_ids)

        if locations:
            for locCode in self.auto_locations.all():
                if self.combination_method == 'intersection':
                    mQs &= locCode.get_member_model_Qs()
                else:
                    mQs |= locCode.get_member_model_Qs()

        return Member.objects.filter(mQs).distinct()
