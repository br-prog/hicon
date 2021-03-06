from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import ListHomeworkForm
from .models import ListHomework
from django.views.generic import DeleteView, UpdateView
import datetime

def account(request):
  try:
    person = User.objects.get(id=request.user.id)
  except:
    return redirect('log')
  else:
    all_el = ListHomework.objects.filter(email=person.email)
    homeworks = []
    for el in all_el:
      homework = el.homework.split(';')
      date = el.date.split(';')
      uns_wd = [ i.split('.') for i in date ]
      days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
      weekdays = []
      for k in uns_wd:
        d = datetime.datetime(int(k[2]), int(k[1]), int(k[0])).weekday()
        weekdays.append(days[d])
      matrix_type = el.matrix_type.split(';')
      data_matrix = []
      for i in matrix_type:
        data_matrix.append(int(i[0]))
      indexs = [i for i in range(len(homework))]
      homeworks.append([el.pk, el.subj.name, zip(homework, matrix_type, date, weekdays, indexs, data_matrix)])

    if request.method == 'POST':
      try:
        form = ListHomeworkForm(request.POST)
        hw = ListHomework.objects.get(email=person.email, subj=form.data['subj'])
      except:
        if form.is_valid():
          new_hw = form.save(commit=False)
          new_hw.email = person.email
          new_hw.subj = form.cleaned_data['subj']
          new_hw.homework = form.cleaned_data['homework']
          new_hw.matrix_type = form.cleaned_data['matrix_type']
          cur_date = form.cleaned_data['date'].split('-')[::-1]
          new_hw.date = '.'.join(cur_date)
          new_hw.save()
          return redirect('account')  
      else:
        old_hw = hw.homework
        old_type = hw.matrix_type
        old_date = hw.date
        cur_date = form.data['date'].split('-')
        new_date = '.'.join(cur_date[::-1])
        ListHomework.objects.filter(subj=hw.subj).update(
          homework = old_hw + ';' + form.data['homework'],
          matrix_type = old_type + ';' + form.data['matrix_type'],
          date = old_date + ';' + new_date
        )
        hw.refresh_from_db()
        return redirect('account')
    else:
      form = ListHomeworkForm()

    context = {
        'acc' : person,
        'form' : form,
        'homeworks' : homeworks
    }
    return render(request, 'account/account.html', context)

class CompleteHomework(DeleteView):
  model = ListHomework
  template_name = 'account/complete.html'
  success_url = '/account/'
  def delete(self, request, *args, **kwargs):
    obj = ListHomework.objects.get(pk=kwargs['pk'])
    cur_hw = obj.homework.split(';')
    cur_hw.pop(kwargs['index'])
    cur_mt = obj.matrix_type.split(';')
    cur_mt.pop(kwargs['index'])
    cur_date = obj.date.split(';')
    cur_date.pop(kwargs['index'])
    if len(cur_hw)==0:
      obj.delete()
      return redirect('account')
    ListHomework.objects.filter(pk=kwargs['pk']).update(
      homework = ';'.join(cur_hw),
      matrix_type = ';'.join(cur_mt),
      date = ';'.join(cur_date)
    )
    obj.refresh_from_db()
    return redirect('account')

class ChangeHomework(UpdateView):
  model = ListHomework
  template_name = 'account/update.html'
  success_url = '/account/'
  form_class = ListHomeworkForm

  def get(self, request, *args, **kwargs):
    obj = ListHomework.objects.get(pk=kwargs['pk'])
    date = obj.date.split(';')[kwargs['index']].split('.')
    form = ListHomeworkForm(
      initial={
        'homework': obj.homework.split(';')[kwargs['index']],
        'matrix_type': obj.matrix_type.split(';')[kwargs['index']]
      }
    )
    context = {
        'form' : form
    }
    return render(request, 'account/update.html', context)

  def post(self, request, *args, **kwargs):
    form = ListHomeworkForm(request.POST)
    obj = ListHomework.objects.get(pk=kwargs['pk'])
    cur_hw = obj.homework.split(';')
    cur_hw[kwargs['index']] = form.data['homework']
    cur_mt = obj.matrix_type.split(';')
    cur_mt[kwargs['index']] = form.data['matrix_type']
    cur_date = obj.date.split(';')
    nof_date = form.data['date'].split('-')
    f_date = '.'.join(nof_date[::-1])
    cur_date[kwargs['index']] = f_date
    ListHomework.objects.filter(pk=kwargs['pk']).update(
      homework = ';'.join(cur_hw),
      matrix_type = ';'.join(cur_mt),
      date = ';'.join(cur_date)
    )
    obj.refresh_from_db()
    return redirect('account')