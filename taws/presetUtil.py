#!/usr/bin/env python
"""
###############################################################################
# MODULE: presetUtil.py
#
# AUTHOR: F.Ippolito
# DATE  : 25/10/2016
#
###############################################################################
"""

import os
import json

#from katelibs.database import TEquipment
from taws.models import TEquipment
#from django.db import connection

import logging,subprocess

logger = logging.getLogger('taws')




class Preset():
    """
    Describe a Preset for specified Test file
    """

    def __init__(self, json_file_name):
        """ Recover the json for specified file
            test_file_name : the test file name
        """
        #prs_file_name = "{:s}/{:s}.json".format(os.path.expanduser(test_area), test_file_name)

        preset_file = open(json_file_name)

        self.__json = json.load(preset_file)
        logger.debug("-- JSON VALUES for file %s"%json_file_name)
        logger.debug(self.__json)
        logger.debug("-------------------------------------\n")


    def get_all_ids(self):
        """ Return a list of ID for current preset file
        """
        id_list = [ ]

        for key in self.__json:
            id_list.append(self.get_id(key))
        logger.debug('get_all_ids function --> %s'%id_list)
        return id_list


    def get_id(self, equip_name):
        """
            Return the equipment Identifier (see K@TE DB, table T_EQUIPMENT)
        """
        try:
            res = self.get_elem(equip_name, "ID")
        except Exception:
            logger.error('get_id function Fail')
            return 'None'
        logger.debug('get_id function --> %s'%str(res))
        return str(res)


    def get_type(self, equip_name):
        """
            Return the equipment Type (see K@TE DB, table T_EQUIPMENT_TYPE)
        """
        try:
            res = self.get_elem(equip_name, "TYPE")
        except Exception:
            res = ""

        return res


    def get_elem(self, equip_name, elem):
        """
            Return a generic element value for specified equipment
        """
        res = ""

        try:
            for item in self.__json[equip_name]:
                if item[0] == elem:
                    res = item[1]
                    break
        except Exception:
            res = ""

        return res

    def __check_id_Family(self, id_eqpt,family):
        """ INTERNAL USAGE """
        try:
            if TEquipment.objects.get(id_equipment=id_eqpt).t_equip_type_id_type.family == family:
                return True
            return False
        except Exception:
            logger.error('Check Id family for id_eqpt = \'%s\' Fail!!'%id_eqpt) 
            return False

    def get_all_ids_family(self,family):
        """ Return a list of ID for current preset file matching family type (i.e. 'EQPT')
        """
        id_list = [ ]
        family_list = [] 
        for key in self.__json:
            id_list.append(self.get_id(key))

        for elem in id_list:
            if self.__check_id_Family(elem,family):
                family_list.append(elem)    
        
        return family_list

