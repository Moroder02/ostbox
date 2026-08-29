from django.shortcuts import render

from ..models import CPU, CPUModel, Disk, DiskModel, RAM, RAMModel, Motherboard, MotherboardModel


def cpu_list(request):
    cpus = CPU.objects.all()
    context = {'cpus': cpus}
    return render(request, 'components/cpu/cpu_list.html', context)


def cpu_model_list(request):
    cpu_models = CPUModel.objects.all()
    context = {'cpu_models': cpu_models}
    return render(request, 'components/cpu/cpu_model.html', context)


def disk_list(request):
    disks = Disk.objects.select_related('disk_model').all()
    allowed_fields = ['disk_model', 'device', 'serial_number']
    obj_fields = [Disk._meta.get_field(name) for name in allowed_fields]
    context = {
        'objects': disks,
        'obj_fields': obj_fields,
    }
    return render(request, 'core/object_list.html', context)


def disk_model_list(request):
    disk_models = DiskModel.objects.all()
    context = {'disk_models': disk_models}
    return render(request, 'components/disk/disk_model.html', context)


def ram_list(request):
    rams = RAM.objects.all()
    context = {'rams': rams}
    return render(request, 'components/ram/ram_list.html', context)


def ram_model_list(request):
    ram_models = RAMModel.objects.all()
    context = {'ram_models': ram_models}
    return render(request, 'components/ram/ram_model.html', context)


def motherboard_list(request):
    motherboards = Motherboard.objects.all()
    context = {'motherboards': motherboards}
    return render(request, 'components/motherboard/motherboard_list.html', context)


def motherboard_model_list(request):
    motherboard_models = MotherboardModel.objects.all()
    context = {'motherboard_models': motherboard_models}
    return render(request, 'components/motherboard/motherboard_model.html', context)
