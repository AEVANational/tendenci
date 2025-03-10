from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=100, blank=True)),
                ('city', models.CharField(max_length=100, blank=True)),
                ('state', models.CharField(max_length=100, blank=True)),
                ('zipcode', models.CharField(max_length=100, blank=True)),
                ('country', models.CharField(max_length=100, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, blank=True)),
                ('addresses', models.ManyToManyField(to='contacts.Address', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allow_anonymous_view', models.BooleanField(default=True, verbose_name='Public can view')),
                ('allow_user_view', models.BooleanField(default=True, verbose_name='Signed in user can view')),
                ('allow_member_view', models.BooleanField(default=True)),
                ('allow_user_edit', models.BooleanField(default=False, verbose_name='Signed in user can change')),
                ('allow_member_edit', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True, verbose_name='Created On')),
                ('update_dt', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('creator_username', models.CharField(max_length=50)),
                ('owner_username', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=True, verbose_name='Active')),
                ('status_detail', models.CharField(default='active', max_length=50)),
                ('guid', models.CharField(max_length=40)),
                ('timezone', timezone_field.fields.TimeZoneField(default='US/Central', max_length=100, choices=[('Pacific/Midway', '(GMT-1100) Pacific/Midway'), ('Pacific/Niue', '(GMT-1100) Pacific/Niue'), ('Pacific/Pago_Pago', '(GMT-1100) Pacific/Pago_Pago'), ('Pacific/Honolulu', '(GMT-1000) Pacific/Honolulu'), ('Pacific/Johnston', '(GMT-1000) Pacific/Johnston'), ('Pacific/Rarotonga', '(GMT-1000) Pacific/Rarotonga'), ('Pacific/Tahiti', '(GMT-1000) Pacific/Tahiti'), ('US/Hawaii', '(GMT-1000) US/Hawaii'), ('Pacific/Marquesas', '(GMT-0930) Pacific/Marquesas'), ('America/Adak', '(GMT-0900) America/Adak'), ('Pacific/Gambier', '(GMT-0900) Pacific/Gambier'), ('America/Anchorage', '(GMT-0800) America/Anchorage'), ('America/Juneau', '(GMT-0800) America/Juneau'), ('America/Metlakatla', '(GMT-0800) America/Metlakatla'), ('America/Nome', '(GMT-0800) America/Nome'), ('America/Sitka', '(GMT-0800) America/Sitka'), ('America/Yakutat', '(GMT-0800) America/Yakutat'), ('Pacific/Pitcairn', '(GMT-0800) Pacific/Pitcairn'), ('US/Alaska', '(GMT-0800) US/Alaska'), ('America/Creston', '(GMT-0700) America/Creston'), ('America/Dawson', '(GMT-0700) America/Dawson'), ('America/Dawson_Creek', '(GMT-0700) America/Dawson_Creek'), ('America/Hermosillo', '(GMT-0700) America/Hermosillo'), ('America/Los_Angeles', '(GMT-0700) America/Los_Angeles'), ('America/Phoenix', '(GMT-0700) America/Phoenix'), ('America/Santa_Isabel', '(GMT-0700) America/Santa_Isabel'), ('America/Tijuana', '(GMT-0700) America/Tijuana'), ('America/Vancouver', '(GMT-0700) America/Vancouver'), ('America/Whitehorse', '(GMT-0700) America/Whitehorse'), ('Canada/Pacific', '(GMT-0700) Canada/Pacific'), ('US/Arizona', '(GMT-0700) US/Arizona'), ('US/Pacific', '(GMT-0700) US/Pacific'), ('America/Belize', '(GMT-0600) America/Belize'), ('America/Boise', '(GMT-0600) America/Boise'), ('America/Cambridge_Bay', '(GMT-0600) America/Cambridge_Bay'), ('America/Chihuahua', '(GMT-0600) America/Chihuahua'), ('America/Costa_Rica', '(GMT-0600) America/Costa_Rica'), ('America/Denver', '(GMT-0600) America/Denver'), ('America/Edmonton', '(GMT-0600) America/Edmonton'), ('America/El_Salvador', '(GMT-0600) America/El_Salvador'), ('America/Guatemala', '(GMT-0600) America/Guatemala'), ('America/Inuvik', '(GMT-0600) America/Inuvik'), ('America/Managua', '(GMT-0600) America/Managua'), ('America/Mazatlan', '(GMT-0600) America/Mazatlan'), ('America/Ojinaga', '(GMT-0600) America/Ojinaga'), ('America/Regina', '(GMT-0600) America/Regina'), ('America/Shiprock', '(GMT-0600) America/Shiprock'), ('America/Swift_Current', '(GMT-0600) America/Swift_Current'), ('America/Tegucigalpa', '(GMT-0600) America/Tegucigalpa'), ('America/Yellowknife', '(GMT-0600) America/Yellowknife'), ('Canada/Mountain', '(GMT-0600) Canada/Mountain'), ('Pacific/Easter', '(GMT-0600) Pacific/Easter'), ('Pacific/Galapagos', '(GMT-0600) Pacific/Galapagos'), ('US/Mountain', '(GMT-0600) US/Mountain'), ('America/Atikokan', '(GMT-0500) America/Atikokan'), ('America/Bahia_Banderas', '(GMT-0500) America/Bahia_Banderas'), ('America/Bogota', '(GMT-0500) America/Bogota'), ('America/Cancun', '(GMT-0500) America/Cancun'), ('America/Cayman', '(GMT-0500) America/Cayman'), ('America/Chicago', '(GMT-0500) America/Chicago'), ('America/Guayaquil', '(GMT-0500) America/Guayaquil'), ('America/Indiana/Knox', '(GMT-0500) America/Indiana/Knox'), ('America/Indiana/Tell_City', '(GMT-0500) America/Indiana/Tell_City'), ('America/Jamaica', '(GMT-0500) America/Jamaica'), ('America/Lima', '(GMT-0500) America/Lima'), ('America/Matamoros', '(GMT-0500) America/Matamoros'), ('America/Menominee', '(GMT-0500) America/Menominee'), ('America/Merida', '(GMT-0500) America/Merida'), ('America/Mexico_City', '(GMT-0500) America/Mexico_City'), ('America/Monterrey', '(GMT-0500) America/Monterrey'), ('America/North_Dakota/Beulah', '(GMT-0500) America/North_Dakota/Beulah'), ('America/North_Dakota/Center', '(GMT-0500) America/North_Dakota/Center'), ('America/North_Dakota/New_Salem', '(GMT-0500) America/North_Dakota/New_Salem'), ('America/Panama', '(GMT-0500) America/Panama'), ('America/Port-au-Prince', '(GMT-0500) America/Port-au-Prince'), ('America/Rainy_River', '(GMT-0500) America/Rainy_River'), ('America/Rankin_Inlet', '(GMT-0500) America/Rankin_Inlet'), ('America/Resolute', '(GMT-0500) America/Resolute'), ('America/Winnipeg', '(GMT-0500) America/Winnipeg'), ('Canada/Central', '(GMT-0500) Canada/Central'), ('US/Central', '(GMT-0500) US/Central'), ('America/Caracas', '(GMT-0430) America/Caracas'), ('America/Anguilla', '(GMT-0400) America/Anguilla'), ('America/Antigua', '(GMT-0400) America/Antigua'), ('America/Aruba', '(GMT-0400) America/Aruba'), ('America/Asuncion', '(GMT-0400) America/Asuncion'), ('America/Barbados', '(GMT-0400) America/Barbados'), ('America/Blanc-Sablon', '(GMT-0400) America/Blanc-Sablon'), ('America/Boa_Vista', '(GMT-0400) America/Boa_Vista'), ('America/Campo_Grande', '(GMT-0400) America/Campo_Grande'), ('America/Cuiaba', '(GMT-0400) America/Cuiaba'), ('America/Curacao', '(GMT-0400) America/Curacao'), ('America/Detroit', '(GMT-0400) America/Detroit'), ('America/Dominica', '(GMT-0400) America/Dominica'), ('America/Eirunepe', '(GMT-0400) America/Eirunepe'), ('America/Grand_Turk', '(GMT-0400) America/Grand_Turk'), ('America/Grenada', '(GMT-0400) America/Grenada'), ('America/Guadeloupe', '(GMT-0400) America/Guadeloupe'), ('America/Guyana', '(GMT-0400) America/Guyana'), ('America/Havana', '(GMT-0400) America/Havana'), ('America/Indiana/Indianapolis', '(GMT-0400) America/Indiana/Indianapolis'), ('America/Indiana/Marengo', '(GMT-0400) America/Indiana/Marengo'), ('America/Indiana/Petersburg', '(GMT-0400) America/Indiana/Petersburg'), ('America/Indiana/Vevay', '(GMT-0400) America/Indiana/Vevay'), ('America/Indiana/Vincennes', '(GMT-0400) America/Indiana/Vincennes'), ('America/Indiana/Winamac', '(GMT-0400) America/Indiana/Winamac'), ('America/Iqaluit', '(GMT-0400) America/Iqaluit'), ('America/Kentucky/Louisville', '(GMT-0400) America/Kentucky/Louisville'), ('America/Kentucky/Monticello', '(GMT-0400) America/Kentucky/Monticello'), ('America/Kralendijk', '(GMT-0400) America/Kralendijk'), ('America/La_Paz', '(GMT-0400) America/La_Paz'), ('America/Lower_Princes', '(GMT-0400) America/Lower_Princes'), ('America/Manaus', '(GMT-0400) America/Manaus'), ('America/Marigot', '(GMT-0400) America/Marigot'), ('America/Martinique', '(GMT-0400) America/Martinique'), ('America/Montreal', '(GMT-0400) America/Montreal'), ('America/Montserrat', '(GMT-0400) America/Montserrat'), ('America/Nassau', '(GMT-0400) America/Nassau'), ('America/New_York', '(GMT-0400) America/New_York'), ('America/Nipigon', '(GMT-0400) America/Nipigon'), ('America/Pangnirtung', '(GMT-0400) America/Pangnirtung'), ('America/Port_of_Spain', '(GMT-0400) America/Port_of_Spain'), ('America/Porto_Velho', '(GMT-0400) America/Porto_Velho'), ('America/Puerto_Rico', '(GMT-0400) America/Puerto_Rico'), ('America/Rio_Branco', '(GMT-0400) America/Rio_Branco'), ('America/Santiago', '(GMT-0400) America/Santiago'), ('America/Santo_Domingo', '(GMT-0400) America/Santo_Domingo'), ('America/St_Barthelemy', '(GMT-0400) America/St_Barthelemy'), ('America/St_Kitts', '(GMT-0400) America/St_Kitts'), ('America/St_Lucia', '(GMT-0400) America/St_Lucia'), ('America/St_Thomas', '(GMT-0400) America/St_Thomas'), ('America/St_Vincent', '(GMT-0400) America/St_Vincent'), ('America/Thunder_Bay', '(GMT-0400) America/Thunder_Bay'), ('America/Toronto', '(GMT-0400) America/Toronto'), ('America/Tortola', '(GMT-0400) America/Tortola'), ('Antarctica/Palmer', '(GMT-0400) Antarctica/Palmer'), ('Canada/Eastern', '(GMT-0400) Canada/Eastern'), ('US/Eastern', '(GMT-0400) US/Eastern'), ('America/Araguaina', '(GMT-0300) America/Araguaina'), ('America/Argentina/Buenos_Aires', '(GMT-0300) America/Argentina/Buenos_Aires'), ('America/Argentina/Catamarca', '(GMT-0300) America/Argentina/Catamarca'), ('America/Argentina/Cordoba', '(GMT-0300) America/Argentina/Cordoba'), ('America/Argentina/Jujuy', '(GMT-0300) America/Argentina/Jujuy'), ('America/Argentina/La_Rioja', '(GMT-0300) America/Argentina/La_Rioja'), ('America/Argentina/Mendoza', '(GMT-0300) America/Argentina/Mendoza'), ('America/Argentina/Rio_Gallegos', '(GMT-0300) America/Argentina/Rio_Gallegos'), ('America/Argentina/Salta', '(GMT-0300) America/Argentina/Salta'), ('America/Argentina/San_Juan', '(GMT-0300) America/Argentina/San_Juan'), ('America/Argentina/San_Luis', '(GMT-0300) America/Argentina/San_Luis'), ('America/Argentina/Tucuman', '(GMT-0300) America/Argentina/Tucuman'), ('America/Argentina/Ushuaia', '(GMT-0300) America/Argentina/Ushuaia'), ('America/Bahia', '(GMT-0300) America/Bahia'), ('America/Belem', '(GMT-0300) America/Belem'), ('America/Cayenne', '(GMT-0300) America/Cayenne'), ('America/Fortaleza', '(GMT-0300) America/Fortaleza'), ('America/Glace_Bay', '(GMT-0300) America/Glace_Bay'), ('America/Goose_Bay', '(GMT-0300) America/Goose_Bay'), ('America/Halifax', '(GMT-0300) America/Halifax'), ('America/Maceio', '(GMT-0300) America/Maceio'), ('America/Moncton', '(GMT-0300) America/Moncton'), ('America/Montevideo', '(GMT-0300) America/Montevideo'), ('America/Paramaribo', '(GMT-0300) America/Paramaribo'), ('America/Recife', '(GMT-0300) America/Recife'), ('America/Santarem', '(GMT-0300) America/Santarem'), ('America/Sao_Paulo', '(GMT-0300) America/Sao_Paulo'), ('America/Thule', '(GMT-0300) America/Thule'), ('Antarctica/Rothera', '(GMT-0300) Antarctica/Rothera'), ('Atlantic/Bermuda', '(GMT-0300) Atlantic/Bermuda'), ('Atlantic/Stanley', '(GMT-0300) Atlantic/Stanley'), ('Canada/Atlantic', '(GMT-0300) Canada/Atlantic'), ('America/St_Johns', '(GMT-0230) America/St_Johns'), ('Canada/Newfoundland', '(GMT-0230) Canada/Newfoundland'), ('America/Godthab', '(GMT-0200) America/Godthab'), ('America/Miquelon', '(GMT-0200) America/Miquelon'), ('America/Noronha', '(GMT-0200) America/Noronha'), ('Atlantic/South_Georgia', '(GMT-0200) Atlantic/South_Georgia'), ('Atlantic/Cape_Verde', '(GMT-0100) Atlantic/Cape_Verde'), ('Africa/Abidjan', '(GMT+0000) Africa/Abidjan'), ('Africa/Accra', '(GMT+0000) Africa/Accra'), ('Africa/Bamako', '(GMT+0000) Africa/Bamako'), ('Africa/Banjul', '(GMT+0000) Africa/Banjul'), ('Africa/Bissau', '(GMT+0000) Africa/Bissau'), ('Africa/Conakry', '(GMT+0000) Africa/Conakry'), ('Africa/Dakar', '(GMT+0000) Africa/Dakar'), ('Africa/El_Aaiun', '(GMT+0000) Africa/El_Aaiun'), ('Africa/Freetown', '(GMT+0000) Africa/Freetown'), ('Africa/Lome', '(GMT+0000) Africa/Lome'), ('Africa/Monrovia', '(GMT+0000) Africa/Monrovia'), ('Africa/Nouakchott', '(GMT+0000) Africa/Nouakchott'), ('Africa/Ouagadougou', '(GMT+0000) Africa/Ouagadougou'), ('Africa/Sao_Tome', '(GMT+0000) Africa/Sao_Tome'), ('America/Danmarkshavn', '(GMT+0000) America/Danmarkshavn'), ('America/Scoresbysund', '(GMT+0000) America/Scoresbysund'), ('Atlantic/Azores', '(GMT+0000) Atlantic/Azores'), ('Atlantic/Reykjavik', '(GMT+0000) Atlantic/Reykjavik'), ('Atlantic/St_Helena', '(GMT+0000) Atlantic/St_Helena'), ('GMT', '(GMT+0000) GMT'), ('UTC', '(GMT+0000) UTC'), ('Africa/Algiers', '(GMT+0100) Africa/Algiers'), ('Africa/Bangui', '(GMT+0100) Africa/Bangui'), ('Africa/Brazzaville', '(GMT+0100) Africa/Brazzaville'), ('Africa/Casablanca', '(GMT+0100) Africa/Casablanca'), ('Africa/Douala', '(GMT+0100) Africa/Douala'), ('Africa/Kinshasa', '(GMT+0100) Africa/Kinshasa'), ('Africa/Lagos', '(GMT+0100) Africa/Lagos'), ('Africa/Libreville', '(GMT+0100) Africa/Libreville'), ('Africa/Luanda', '(GMT+0100) Africa/Luanda'), ('Africa/Malabo', '(GMT+0100) Africa/Malabo'), ('Africa/Ndjamena', '(GMT+0100) Africa/Ndjamena'), ('Africa/Niamey', '(GMT+0100) Africa/Niamey'), ('Africa/Porto-Novo', '(GMT+0100) Africa/Porto-Novo'), ('Africa/Tunis', '(GMT+0100) Africa/Tunis'), ('Africa/Windhoek', '(GMT+0100) Africa/Windhoek'), ('Atlantic/Canary', '(GMT+0100) Atlantic/Canary'), ('Atlantic/Faroe', '(GMT+0100) Atlantic/Faroe'), ('Atlantic/Madeira', '(GMT+0100) Atlantic/Madeira'), ('Europe/Dublin', '(GMT+0100) Europe/Dublin'), ('Europe/Guernsey', '(GMT+0100) Europe/Guernsey'), ('Europe/Isle_of_Man', '(GMT+0100) Europe/Isle_of_Man'), ('Europe/Jersey', '(GMT+0100) Europe/Jersey'), ('Europe/Lisbon', '(GMT+0100) Europe/Lisbon'), ('Europe/London', '(GMT+0100) Europe/London'), ('Africa/Blantyre', '(GMT+0200) Africa/Blantyre'), ('Africa/Bujumbura', '(GMT+0200) Africa/Bujumbura'), ('Africa/Cairo', '(GMT+0200) Africa/Cairo'), ('Africa/Ceuta', '(GMT+0200) Africa/Ceuta'), ('Africa/Gaborone', '(GMT+0200) Africa/Gaborone'), ('Africa/Harare', '(GMT+0200) Africa/Harare'), ('Africa/Johannesburg', '(GMT+0200) Africa/Johannesburg'), ('Africa/Kigali', '(GMT+0200) Africa/Kigali'), ('Africa/Lubumbashi', '(GMT+0200) Africa/Lubumbashi'), ('Africa/Lusaka', '(GMT+0200) Africa/Lusaka'), ('Africa/Maputo', '(GMT+0200) Africa/Maputo'), ('Africa/Maseru', '(GMT+0200) Africa/Maseru'), ('Africa/Mbabane', '(GMT+0200) Africa/Mbabane'), ('Africa/Tripoli', '(GMT+0200) Africa/Tripoli'), ('Arctic/Longyearbyen', '(GMT+0200) Arctic/Longyearbyen'), ('Asia/Gaza', '(GMT+0200) Asia/Gaza'), ('Asia/Hebron', '(GMT+0200) Asia/Hebron'), ('Europe/Amsterdam', '(GMT+0200) Europe/Amsterdam'), ('Europe/Andorra', '(GMT+0200) Europe/Andorra'), ('Europe/Belgrade', '(GMT+0200) Europe/Belgrade'), ('Europe/Berlin', '(GMT+0200) Europe/Berlin'), ('Europe/Bratislava', '(GMT+0200) Europe/Bratislava'), ('Europe/Brussels', '(GMT+0200) Europe/Brussels'), ('Europe/Budapest', '(GMT+0200) Europe/Budapest'), ('Europe/Copenhagen', '(GMT+0200) Europe/Copenhagen'), ('Europe/Gibraltar', '(GMT+0200) Europe/Gibraltar'), ('Europe/Ljubljana', '(GMT+0200) Europe/Ljubljana'), ('Europe/Luxembourg', '(GMT+0200) Europe/Luxembourg'), ('Europe/Madrid', '(GMT+0200) Europe/Madrid'), ('Europe/Malta', '(GMT+0200) Europe/Malta'), ('Europe/Monaco', '(GMT+0200) Europe/Monaco'), ('Europe/Oslo', '(GMT+0200) Europe/Oslo'), ('Europe/Paris', '(GMT+0200) Europe/Paris'), ('Europe/Podgorica', '(GMT+0200) Europe/Podgorica'), ('Europe/Prague', '(GMT+0200) Europe/Prague'), ('Europe/Rome', '(GMT+0200) Europe/Rome'), ('Europe/San_Marino', '(GMT+0200) Europe/San_Marino'), ('Europe/Sarajevo', '(GMT+0200) Europe/Sarajevo'), ('Europe/Skopje', '(GMT+0200) Europe/Skopje'), ('Europe/Stockholm', '(GMT+0200) Europe/Stockholm'), ('Europe/Tirane', '(GMT+0200) Europe/Tirane'), ('Europe/Vaduz', '(GMT+0200) Europe/Vaduz'), ('Europe/Vatican', '(GMT+0200) Europe/Vatican'), ('Europe/Vienna', '(GMT+0200) Europe/Vienna'), ('Europe/Warsaw', '(GMT+0200) Europe/Warsaw'), ('Europe/Zagreb', '(GMT+0200) Europe/Zagreb'), ('Europe/Zurich', '(GMT+0200) Europe/Zurich'), ('Africa/Addis_Ababa', '(GMT+0300) Africa/Addis_Ababa'), ('Africa/Asmara', '(GMT+0300) Africa/Asmara'), ('Africa/Dar_es_Salaam', '(GMT+0300) Africa/Dar_es_Salaam'), ('Africa/Djibouti', '(GMT+0300) Africa/Djibouti'), ('Africa/Juba', '(GMT+0300) Africa/Juba'), ('Africa/Kampala', '(GMT+0300) Africa/Kampala'), ('Africa/Khartoum', '(GMT+0300) Africa/Khartoum'), ('Africa/Mogadishu', '(GMT+0300) Africa/Mogadishu'), ('Africa/Nairobi', '(GMT+0300) Africa/Nairobi'), ('Antarctica/Syowa', '(GMT+0300) Antarctica/Syowa'), ('Asia/Aden', '(GMT+0300) Asia/Aden'), ('Asia/Amman', '(GMT+0300) Asia/Amman'), ('Asia/Baghdad', '(GMT+0300) Asia/Baghdad'), ('Asia/Bahrain', '(GMT+0300) Asia/Bahrain'), ('Asia/Beirut', '(GMT+0300) Asia/Beirut'), ('Asia/Damascus', '(GMT+0300) Asia/Damascus'), ('Asia/Jerusalem', '(GMT+0300) Asia/Jerusalem'), ('Asia/Kuwait', '(GMT+0300) Asia/Kuwait'), ('Asia/Nicosia', '(GMT+0300) Asia/Nicosia'), ('Asia/Qatar', '(GMT+0300) Asia/Qatar'), ('Asia/Riyadh', '(GMT+0300) Asia/Riyadh'), ('Europe/Athens', '(GMT+0300) Europe/Athens'), ('Europe/Bucharest', '(GMT+0300) Europe/Bucharest'), ('Europe/Chisinau', '(GMT+0300) Europe/Chisinau'), ('Europe/Helsinki', '(GMT+0300) Europe/Helsinki'), ('Europe/Istanbul', '(GMT+0300) Europe/Istanbul'), ('Europe/Kaliningrad', '(GMT+0300) Europe/Kaliningrad'), ('Europe/Kiev', '(GMT+0300) Europe/Kiev'), ('Europe/Mariehamn', '(GMT+0300) Europe/Mariehamn'), ('Europe/Minsk', '(GMT+0300) Europe/Minsk'), ('Europe/Riga', '(GMT+0300) Europe/Riga'), ('Europe/Simferopol', '(GMT+0300) Europe/Simferopol'), ('Europe/Sofia', '(GMT+0300) Europe/Sofia'), ('Europe/Tallinn', '(GMT+0300) Europe/Tallinn'), ('Europe/Uzhgorod', '(GMT+0300) Europe/Uzhgorod'), ('Europe/Vilnius', '(GMT+0300) Europe/Vilnius'), ('Europe/Zaporozhye', '(GMT+0300) Europe/Zaporozhye'), ('Indian/Antananarivo', '(GMT+0300) Indian/Antananarivo'), ('Indian/Comoro', '(GMT+0300) Indian/Comoro'), ('Indian/Mayotte', '(GMT+0300) Indian/Mayotte'), ('Asia/Dubai', '(GMT+0400) Asia/Dubai'), ('Asia/Muscat', '(GMT+0400) Asia/Muscat'), ('Asia/Tbilisi', '(GMT+0400) Asia/Tbilisi'), ('Asia/Yerevan', '(GMT+0400) Asia/Yerevan'), ('Europe/Moscow', '(GMT+0400) Europe/Moscow'), ('Europe/Samara', '(GMT+0400) Europe/Samara'), ('Europe/Volgograd', '(GMT+0400) Europe/Volgograd'), ('Indian/Mahe', '(GMT+0400) Indian/Mahe'), ('Indian/Mauritius', '(GMT+0400) Indian/Mauritius'), ('Indian/Reunion', '(GMT+0400) Indian/Reunion'), ('Asia/Kabul', '(GMT+0430) Asia/Kabul'), ('Asia/Tehran', '(GMT+0430) Asia/Tehran'), ('Antarctica/Mawson', '(GMT+0500) Antarctica/Mawson'), ('Asia/Aqtau', '(GMT+0500) Asia/Aqtau'), ('Asia/Aqtobe', '(GMT+0500) Asia/Aqtobe'), ('Asia/Ashgabat', '(GMT+0500) Asia/Ashgabat'), ('Asia/Baku', '(GMT+0500) Asia/Baku'), ('Asia/Dushanbe', '(GMT+0500) Asia/Dushanbe'), ('Asia/Karachi', '(GMT+0500) Asia/Karachi'), ('Asia/Oral', '(GMT+0500) Asia/Oral'), ('Asia/Samarkand', '(GMT+0500) Asia/Samarkand'), ('Asia/Tashkent', '(GMT+0500) Asia/Tashkent'), ('Indian/Kerguelen', '(GMT+0500) Indian/Kerguelen'), ('Indian/Maldives', '(GMT+0500) Indian/Maldives'), ('Asia/Colombo', '(GMT+0530) Asia/Colombo'), ('Asia/Kolkata', '(GMT+0530) Asia/Kolkata'), ('Asia/Kathmandu', '(GMT+0545) Asia/Kathmandu'), ('Antarctica/Vostok', '(GMT+0600) Antarctica/Vostok'), ('Asia/Almaty', '(GMT+0600) Asia/Almaty'), ('Asia/Bishkek', '(GMT+0600) Asia/Bishkek'), ('Asia/Dhaka', '(GMT+0600) Asia/Dhaka'), ('Asia/Qyzylorda', '(GMT+0600) Asia/Qyzylorda'), ('Asia/Thimphu', '(GMT+0600) Asia/Thimphu'), ('Asia/Yekaterinburg', '(GMT+0600) Asia/Yekaterinburg'), ('Indian/Chagos', '(GMT+0600) Indian/Chagos'), ('Asia/Rangoon', '(GMT+0630) Asia/Rangoon'), ('Indian/Cocos', '(GMT+0630) Indian/Cocos'), ('Antarctica/Davis', '(GMT+0700) Antarctica/Davis'), ('Asia/Bangkok', '(GMT+0700) Asia/Bangkok'), ('Asia/Ho_Chi_Minh', '(GMT+0700) Asia/Ho_Chi_Minh'), ('Asia/Hovd', '(GMT+0700) Asia/Hovd'), ('Asia/Jakarta', '(GMT+0700) Asia/Jakarta'), ('Asia/Novokuznetsk', '(GMT+0700) Asia/Novokuznetsk'), ('Asia/Novosibirsk', '(GMT+0700) Asia/Novosibirsk'), ('Asia/Omsk', '(GMT+0700) Asia/Omsk'), ('Asia/Phnom_Penh', '(GMT+0700) Asia/Phnom_Penh'), ('Asia/Pontianak', '(GMT+0700) Asia/Pontianak'), ('Asia/Vientiane', '(GMT+0700) Asia/Vientiane'), ('Indian/Christmas', '(GMT+0700) Indian/Christmas'), ('Antarctica/Casey', '(GMT+0800) Antarctica/Casey'), ('Asia/Brunei', '(GMT+0800) Asia/Brunei'), ('Asia/Choibalsan', '(GMT+0800) Asia/Choibalsan'), ('Asia/Chongqing', '(GMT+0800) Asia/Chongqing'), ('Asia/Harbin', '(GMT+0800) Asia/Harbin'), ('Asia/Hong_Kong', '(GMT+0800) Asia/Hong_Kong'), ('Asia/Kashgar', '(GMT+0800) Asia/Kashgar'), ('Asia/Krasnoyarsk', '(GMT+0800) Asia/Krasnoyarsk'), ('Asia/Kuala_Lumpur', '(GMT+0800) Asia/Kuala_Lumpur'), ('Asia/Kuching', '(GMT+0800) Asia/Kuching'), ('Asia/Macau', '(GMT+0800) Asia/Macau'), ('Asia/Makassar', '(GMT+0800) Asia/Makassar'), ('Asia/Manila', '(GMT+0800) Asia/Manila'), ('Asia/Shanghai', '(GMT+0800) Asia/Shanghai'), ('Asia/Singapore', '(GMT+0800) Asia/Singapore'), ('Asia/Taipei', '(GMT+0800) Asia/Taipei'), ('Asia/Ulaanbaatar', '(GMT+0800) Asia/Ulaanbaatar'), ('Asia/Urumqi', '(GMT+0800) Asia/Urumqi'), ('Australia/Perth', '(GMT+0800) Australia/Perth'), ('Australia/Eucla', '(GMT+0845) Australia/Eucla'), ('Asia/Dili', '(GMT+0900) Asia/Dili'), ('Asia/Irkutsk', '(GMT+0900) Asia/Irkutsk'), ('Asia/Jayapura', '(GMT+0900) Asia/Jayapura'), ('Asia/Pyongyang', '(GMT+0900) Asia/Pyongyang'), ('Asia/Seoul', '(GMT+0900) Asia/Seoul'), ('Asia/Tokyo', '(GMT+0900) Asia/Tokyo'), ('Pacific/Palau', '(GMT+0900) Pacific/Palau'), ('Australia/Adelaide', '(GMT+0930) Australia/Adelaide'), ('Australia/Broken_Hill', '(GMT+0930) Australia/Broken_Hill'), ('Australia/Darwin', '(GMT+0930) Australia/Darwin'), ('Antarctica/DumontDUrville', '(GMT+1000) Antarctica/DumontDUrville'), ('Asia/Yakutsk', '(GMT+1000) Asia/Yakutsk'), ('Australia/Brisbane', '(GMT+1000) Australia/Brisbane'), ('Australia/Currie', '(GMT+1000) Australia/Currie'), ('Australia/Hobart', '(GMT+1000) Australia/Hobart'), ('Australia/Lindeman', '(GMT+1000) Australia/Lindeman'), ('Australia/Melbourne', '(GMT+1000) Australia/Melbourne'), ('Australia/Sydney', '(GMT+1000) Australia/Sydney'), ('Pacific/Chuuk', '(GMT+1000) Pacific/Chuuk'), ('Pacific/Guam', '(GMT+1000) Pacific/Guam'), ('Pacific/Port_Moresby', '(GMT+1000) Pacific/Port_Moresby'), ('Pacific/Saipan', '(GMT+1000) Pacific/Saipan'), ('Australia/Lord_Howe', '(GMT+1030) Australia/Lord_Howe'), ('Antarctica/Macquarie', '(GMT+1100) Antarctica/Macquarie'), ('Asia/Sakhalin', '(GMT+1100) Asia/Sakhalin'), ('Asia/Vladivostok', '(GMT+1100) Asia/Vladivostok'), ('Pacific/Efate', '(GMT+1100) Pacific/Efate'), ('Pacific/Guadalcanal', '(GMT+1100) Pacific/Guadalcanal'), ('Pacific/Kosrae', '(GMT+1100) Pacific/Kosrae'), ('Pacific/Noumea', '(GMT+1100) Pacific/Noumea'), ('Pacific/Pohnpei', '(GMT+1100) Pacific/Pohnpei'), ('Pacific/Norfolk', '(GMT+1130) Pacific/Norfolk'), ('Antarctica/McMurdo', '(GMT+1200) Antarctica/McMurdo'), ('Antarctica/South_Pole', '(GMT+1200) Antarctica/South_Pole'), ('Asia/Anadyr', '(GMT+1200) Asia/Anadyr'), ('Asia/Kamchatka', '(GMT+1200) Asia/Kamchatka'), ('Asia/Magadan', '(GMT+1200) Asia/Magadan'), ('Pacific/Auckland', '(GMT+1200) Pacific/Auckland'), ('Pacific/Fiji', '(GMT+1200) Pacific/Fiji'), ('Pacific/Funafuti', '(GMT+1200) Pacific/Funafuti'), ('Pacific/Kwajalein', '(GMT+1200) Pacific/Kwajalein'), ('Pacific/Majuro', '(GMT+1200) Pacific/Majuro'), ('Pacific/Nauru', '(GMT+1200) Pacific/Nauru'), ('Pacific/Tarawa', '(GMT+1200) Pacific/Tarawa'), ('Pacific/Wake', '(GMT+1200) Pacific/Wake'), ('Pacific/Wallis', '(GMT+1200) Pacific/Wallis'), ('Pacific/Chatham', '(GMT+1245) Pacific/Chatham'), ('Pacific/Apia', '(GMT+1300) Pacific/Apia'), ('Pacific/Enderbury', '(GMT+1300) Pacific/Enderbury'), ('Pacific/Fakaofo', '(GMT+1300) Pacific/Fakaofo'), ('Pacific/Tongatapu', '(GMT+1300) Pacific/Tongatapu'), ('Pacific/Kiritimati', '(GMT+1400) Pacific/Kiritimati')])),
                ('first_name', models.CharField(max_length=100, blank=True)),
                ('middle_name', models.CharField(max_length=100, blank=True)),
                ('last_name', models.CharField(max_length=100, blank=True)),
                ('suffix', models.CharField(max_length=5, blank=True)),
                ('message', models.TextField()),
                ('addresses', models.ManyToManyField(to='contacts.Address', blank=True)),
                ('companies', models.ManyToManyField(to='contacts.Company', blank=True)),
                ('creator', models.ForeignKey(related_name='%(app_label)s_%(class)s_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=50, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
            ],
        ),
        migrations.AddField(
            model_name='contact',
            name='emails',
            field=models.ManyToManyField(to='contacts.Email', blank=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='entity',
            field=models.ForeignKey(related_name='%(app_label)s_%(class)s_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='owner',
            field=models.ForeignKey(related_name='%(app_label)s_%(class)s_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='phones',
            field=models.ManyToManyField(to='contacts.Phone', blank=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='urls',
            field=models.ManyToManyField(to='contacts.URL', blank=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='user',
            field=models.ForeignKey(related_name='contact_user', to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='company',
            name='emails',
            field=models.ManyToManyField(to='contacts.Email', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='phones',
            field=models.ManyToManyField(to='contacts.Phone', blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='urls',
            field=models.ManyToManyField(to='contacts.URL', blank=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='contact',
            field=models.ForeignKey(related_name='comments', to='contacts.Contact', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='comment',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='contact_comments', on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
