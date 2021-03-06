#
# Copyright 2008 Darrel Herbst
#
# This file is part of Django-Rabid-Ratings.
#
# Django-Rabid-Ratings is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Django-Rabid-Ratings is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Django-Rabid-Ratings.  If not, see <http://www.gnu.org/licenses/>.
#
from django.contrib import admin
from rabidratings.models import Rating, RatingEvent


class RatingAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'avg_rating', 'updated',)


class RatingEventAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'user', 'value', 'updated',)

admin.site.register(Rating, RatingAdmin)
admin.site.register(RatingEvent, RatingEventAdmin)
