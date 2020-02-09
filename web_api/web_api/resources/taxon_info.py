from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal

from web_api.resources import auth
from web_api.common.util import abort_if_record_doesnt_exist, get_all_records, get_record_by_ID, update_record, delete_record 
from web_api.models import TaxonInfo, db


taxon_info_fields = {
    'taxon': fields.Integer,
    'description_1': fields.String,
    'description_2': fields.String,
    'description_3': fields.String,
    'uri': fields.Url('taxon_info', absolute=True, scheme='http')
}

class TaxonInfoListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('taxon', type = int)
        self.reqparse.add_argument('description_1', type = str)
        self.reqparse.add_argument('description_2', type = str)
        self.reqparse.add_argument('description_3', type = str)

        super(TaxonInfoListAPI, self).__init__()

    def get(self):
        output = get_all_records(TaxonInfo, "taxon_info")
        return {'data' : marshal(output, taxon_info_fields)}

    def post(self):
        args = self.reqparse.parse_args()
        
        taxon = args['taxon']
        description_1 = args['description_1']
        description_2 = args['description_2']
        description_3 = args['description_3']
        
        new_row = TaxonInfo(taxon, description_1, description_2, description_3)
        db.session.add(new_row)
        db.session.commit()
        new_row_id = new_row.id
        return new_row_id, 201


class TaxonInfoAPI(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('taxon', type = int)
        self.reqparse.add_argument('description_1', type = str)
        self.reqparse.add_argument('description_2', type = str)
        self.reqparse.add_argument('description_3', type = str)
        super(TaxonInfoAPI, self).__init__()    

    def get(self, id):
        output = get_record_by_ID(TaxonInfo, id, "taxon_info")
        return {'data' : marshal(output, taxon_info_fields)}

    def delete(self, id):
        delete_record(TaxonInfo, id)     
        return '', 204

    def put(self, id):
        args = self.reqparse.parse_args()
        output = update_record(TaxonInfo, id, args, "taxon_info")
        return output, 201

#POST
#curl -u ubiome:welovebacteria http://localhost:5000/api/v0/taxon_info -d "taxon=1&description_1=Streptococcus bacteria are among the most abundant in our microbiomes, and they are the predominant microbes in our mouths and throats.&description_2=Most streptococci are completely harmless and not even capable of causing disease in humans, but a handful of strains can be pathogenic, such as those which cause strep throat.&description_3=About a third of women have Streptococcus agalactiae (also known as Group B streptococcus or GBS) in their vaginal microbiomes.  Although this strain is largely harmless to adults, it can cause serious infections in newborns who acquire it during birth.  For this reason, third-trimester screening for GBS is a standard component of pre-natal care, moms who test GBS positive are given a prophylactic antibiotic right before delivery, and the babies are born free of infection." -X POST -v
#PUT 
#curl -u ubiome:welovebacteria http://localhost:5000/api/v0/taxon_info/1 -d "taxon=2&description_1=Streptococcus bacteria are among the most abundant in our microbiomes, and they are the predominant microbes in our mouths and throats.&description_2=Most streptococci are completely harmless and not even capable of causing disease in humans, but a handful of strains can be pathogenic, such as those which cause strep throat.&description_3=About a third of women have Streptococcus agalactiae (also known as Group B streptococcus or GBS) in their vaginal microbiomes.  Although this strain is largely harmless to adults, it can cause serious infections in newborns who acquire it during birth.  For this reason, third-trimester screening for GBS is a standard component of pre-natal care, moms who test GBS positive are given a prophylactic antibiotic right before delivery, and the babies are born free of infect" -X PUT -v
#curl -u ubiome:welovebacteria http://localhost:5000/api/v0/taxa (GET ALL)
#curl -u ubiome:welovebacteria http://localhost:5000/api/v0/taxa/2 (GET ONE)
#curl -u ubiome:welovebacteria http://localhost:5000/api/v0/taxon_info/1 -X DELETE -v