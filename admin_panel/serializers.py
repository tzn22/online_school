from rest_framework import serializers
from .models import AdminActionLog, ReportTemplate, GeneratedReport, MassEmailCampaign, SystemSetting
from accounts.models import User

class AdminActionLogSerializer(serializers.ModelSerializer):
    admin_user_name = serializers.CharField(source='admin_user.get_full_name', read_only=True)
    
    class Meta:
        model = AdminActionLog
        fields = '__all__'
        read_only_fields = ['created_at', 'admin_user']

class ReportTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by']

class GeneratedReportSerializer(serializers.ModelSerializer):
    report_template_name = serializers.CharField(source='report_template.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
    class Meta:
        model = GeneratedReport
        fields = '__all__'
        read_only_fields = ['generated_at', 'generated_by', 'file_size']

class MassEmailCampaignSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = MassEmailCampaign
        fields = '__all__'
        read_only_fields = [
            'created_at', 'updated_at', 'sent_at', 'completed_at',
            'total_recipients', 'sent_count', 'failed_count', 'success_rate'
        ]
    
    def get_success_rate(self, obj):
        return obj.success_rate

class SystemSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_key(self, value):
        if SystemSetting.objects.filter(key=value).exists():
            raise serializers.ValidationError('Настройка с таким ключом уже существует')
        return value
    
    def validate_value(self, value):
        # Здесь можно добавить валидацию в зависимости от типа настройки
        return value