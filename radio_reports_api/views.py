from os.path import basename, join
import json

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import status

from radio_reports_api.cache import (
    create_folder_in_cache,
    delete_from_cache,
    save_file_to_cache,
)
from radio_reports_api.cloud_storage import (
    upload_to_cloud_storage_from_cache,
)
from radio_reports_api.utils import (
    select_random_segment_names,
    reverse_words_in_str,
)
from radio_reports_api.serializers import (
    ReportSerializer,
)
from radio_reports_api.tasks import generate_report_text_and_model
from radio_reports.settings import CACHE_ROOT, ADMIN_SECRET
# from radio_reports_api.tasks.nifti_to_segmentation import run_total_segmentator_on_nii_image
# from radio_reports_api.tasks.segmentation_to_mesh import total_segmentator_output_to_objs, segment_names
from radio_reports_api.utils import unique_str
from radio_reports_api.models import Report


class AddReportAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request):
        admin_secret_header = request.headers.get('X-AD-ADMIN-SECRET')
        if not admin_secret_header == ADMIN_SECRET:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        
        nifti_image_file = request.FILES.get('niftiImage')
        report_data = request.data.get('reportData')
        report_metadata = request.data.get('reportMetadata')

        report_media_id = unique_str()
        nii_file_name, nii_file_path = save_file_to_cache(nifti_image_file, report_media_id)
        
        new_report = Report.objects.create(
            report_media_id=report_media_id,
            report_metadata=report_metadata,
            meshes_metadata=json.dumps({}),
            original_report=report_data,
            simplified_reports=json.dumps({}),
            processing_status="Initializing..."
        )

        generate_report_text_and_model(
            new_report.id,
            report_media_id,
            nii_file_name,
            report_data,
            nifti_image_file.name
        )

        return Response({
            'success': True,
            'result': {
                'reportId': new_report.id,
                'qrCode': "foo",
                'reportLink': "bar",
            },
        }, status=status.HTTP_201_CREATED)


class GetReportAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        report_id = request.data.get('reportId')
        # report_passcode = request.data.get('reportPasscode')
        # validate above 1

        try:
            report = Report.objects.get(id=report_id)
            report_serializer = ReportSerializer(report)
        except:
            return Response({
                'success': False,
                'error': {
                    'code': -1,
                    'message': "Invalid reportId"
                },
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'success': True,
            'result': {
                'report': report_serializer.data,
            },
        }, status=status.HTTP_200_OK)


class AskQuestionBasedOnReportAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request):
        report_id = request.data.get('reportId', None)
        language = request.data.get('language', None)
        # TODO: return bad response if reportId not given

        try:
            report_object = Report.objects.get(id=report_id)
        except:
            return Response({
                'success': False,
                'error': {
                    'code': -1,
                    'message': "Invalid reportId"
                },
            }, status=status.HTTP_404_NOT_FOUND)


        question_text = request.data.get('questionText', None)
        if question_text is None:
            question_audio = request.FILES.get('questionAudio', None)
            if question_audio is None:
                return Response({
                    'success': False,
                    'error': {
                        'code': -1,
                        'message': "Either questionText or questionAudio must be provided",
                    }
                })
            # convert question_audio to text
        
        original_report_data = report_object.original_report
        simplified_reports = json.loads(report_object.simplified_reports)
        
        # TODO: get the answer from the LLM - pass language as a param too
        answer = reverse_words_in_str(question_text)

        return Response({
            'success': True,
            'result': {
                'answer': answer,
            },
        })
    