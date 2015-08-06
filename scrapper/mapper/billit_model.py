#-*- coding: utf-8 -*-

class Bill(object):
    '''
    class bassed on the model from
    bill-it/app/models/bill.rb

    '''
    uid= "" #type: String
    title= "" #, type: String
    abstract= "" #, type: String
    creation_date= "" #, type: Time
    source= "" #, type: String
    initial_chamber= "" #, type: String
    stage= "" #, type: String
    sub_stage= "" #, type: String
    status= "" #, type: String
    resulting_document= "" #, type: String
    merged_bills= "" #, type: Array
    subject_areas= "" #, type: Array
    authors= "" #, type: Array
    publish_date= "" #, type: Time
    tags= "" #, type: Array
    bill_draft_link= "" #, type: String
    current_priority= "" #, type: String


class Paperwork(object):

  session = ''#, :type => String
  date = ''#, :type => DateTime
  description = ''#, :type => String
  stage = ''#, :type => String
  chamber = ''#, :type => String
  bill_uid = ''#, :type => String
  timeline_status = ''#, :type => String


class Directive(object):
    pass

class Document(object):
    pass
