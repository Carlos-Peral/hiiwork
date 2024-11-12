from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404
from apps.gigs.models import Gig, UserFile, RequirementClient
# Create your views here.

GIG_CREATION_URL_MODIFIER = 'gig-media'
REQUIREMENT_DELIVERY_URL_MODIFIER = 'order-media'
GIG_CREATION_SOURCE = 'gig-creation'
REQUIREMENT_DELIVERY_SOURCE = 'requirement-delivery'


def uploadFile(request):
    try:
        # There is just a small number of endpoints from where they can upload
        # files, each one is specified in 'source'
        source = request.POST.get('source')

        if source == GIG_CREATION_SOURCE:
            # Check if there is an unfinished gig by that PK and then  if there are
            # available slots of images to upload for that gig.
            gigPK = int(request.POST.get('key'))
            gig = get_object_or_404(Gig, pk=gigPK)
            if gig.isFinished == False and gig.author == request.user:
                files_already_saved = gig.files.all()
                if len(list(files_already_saved)) > 9:
                    return HttpResponseForbidden()

                # TODO: Check if  the  file extension is allowed and other limits like size

                # Now  we can savee the files.
                file_from_web = request.FILES.get('files')
                file_to_save = UserFile()
                file_to_save.propietary = request.user
                file_to_save.isPrivate = False
                file_to_save.url_modifier = GIG_CREATION_URL_MODIFIER
                file_to_save.save()
                gig.files.add(file_to_save)
                # Save the relationship first and then start uploading the file
                file_to_save.publicFile = file_from_web
                file_to_save.fileExtension = file_from_web.name.split(
                    '.')[-1]
                file_to_save.save()

                return HttpResponse(content=str(file_to_save.pk))
            else:
                return HttpResponseForbidden()

        elif source == REQUIREMENT_DELIVERY_SOURCE:
            # Check if there is an unfinished gig by that PK and then  if there are
            # available slots of images to upload for that gig.
            clientRequirementPK = int(request.POST.get('key'))
            clientRequirement = get_object_or_404(
                RequirementClient, pk=clientRequirementPK)
            if clientRequirement.delivered == False and clientRequirement.order.buyer == request.user:

                files_already_saved = clientRequirement.files.all()
                if len(list(files_already_saved)) > 9:
                    return HttpResponseForbidden()

                # TODO: Check limits like size

                # Now  we can save the file.
                file_from_web = request.FILES.get('files')
                file_to_save = UserFile()
                file_to_save.propietary = request.user
                file_to_save.isPrivate = True
                file_to_save.url_modifier = REQUIREMENT_DELIVERY_URL_MODIFIER
                file_to_save.save()
                file_to_save.sharedWith.add(clientRequirement.order.seller)
                clientRequirement.files.add(file_to_save)
                # Save the relationship first and then start uploading the file
                file_to_save.privateFile = file_from_web
                file_to_save.fileExtension = file_from_web.name.split(
                    '.')[-1]
                file_to_save.save()
                return HttpResponse(content=str(file_to_save.pk))
        else:
            return HttpResponseForbidden()
    except Exception as e:
        return HttpResponseForbidden()


def deleteFile(request):
    try:
        # The user can delete it's file only if it is not being shared with anyone.
        filePK = int(request.body)
        file_to_delete = get_object_or_404(UserFile, pk=filePK)
        if len(list(file_to_delete.sharedWith.all())) == 0 and file_to_delete.propietary == request.user:
            file_to_delete.delete()
            return HttpResponse(content='Files succesfully deleted.')
        else:
            return HttpResponseForbidden()
    except:
        return HttpResponseForbidden()
