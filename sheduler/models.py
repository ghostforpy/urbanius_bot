from django.db import models

# Create your models here.
class TaskTypes(models.Model):
    code = models.CharField("Код типа задания", unique=True, max_length=150, blank=False)
    name = models.CharField("Тип задания", max_length=150, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Типы заданий' 
        verbose_name = 'Тип задания' 
        ordering = ['name']

class Tasks(models.Model):
    code = models.CharField("Код задания", unique=True, max_length=150, blank=False)
    name = models.CharField("Имя задания", unique=True, max_length=150, blank=False)
    task_type = models.ForeignKey(TaskTypes,on_delete=models.PROTECT, verbose_name="Тип задания", null=True)
    date = models.DateField("Дата запуска", blank=True, null=True)
    time = models.TimeField("Время запуска", blank=True, null=True)
    # Ежедневный запуск
    mon = models.BooleanField("пн", default=False)
    tue = models.BooleanField("вт", default=False)
    wed = models.BooleanField("ср", default=False)
    thu = models.BooleanField("чт", default=False)
    fri = models.BooleanField("пт", default=False)
    sat = models.BooleanField("сб", default=False)
    san = models.BooleanField("вс", default=False)
    # Ежемесячный запуск
    day = models.IntegerField("День месяца", null = True, blank=True)
    # Постоянное задание
    interval = models.IntegerField("интервал выполнения, сек.", null = True, blank=True)
    is_active = models.BooleanField("Активно", default=False)
    def __str__(self):
        return self.name + " " + str(self.task_type)
    def getdays(self):
        res = []
        if self.mon: res.append(0)
        if self.tue: res.append(1)
        if self.wed: res.append(2)
        if self.thu: res.append(3)
        if self.fri: res.append(4)
        if self.sat: res.append(5)
        if self.san: res.append(6)
        return tuple(res)

    class Meta:
        verbose_name_plural = 'Задания' 
        verbose_name = 'Задание' 
        ordering = ['name']