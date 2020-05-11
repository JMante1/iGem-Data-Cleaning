# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 13:22:23 2020

@author: JVM
"""
import requests
import os



#https://synbiohub.org/public/igem/BBa_I11031/1

#/var/www/html/examples/pages

#function serverRequest($jsonRequest)
#{
#  $context = new ZMQContext();
#  $requester = new ZMQSocket($context, ZMQ::SOCKET_REQ);
#  $requester->connect("tcp://localhost:5556");
#  $requester->send(json_encode($jsonRequest));
#  return json_decode($requester->recv());
#}

#http://song.ece.utah.edu/:5556
#"tcp://localhost:5556"


##data to send
#data = {"textToUpload": fasta_text,
#        "detectFeatures": detect,
#        "textId": partname,
#        "textName": partname,
#        "topology": linearity} 
##parameters to send
#params ={} 
#
##post data to snapgene server
#requests.post(newtext_url, data = data, params = params,  headers = {"Accept":"text/plain"})
    
post_url = 'http://song.ece.utah.edu/:5556'

cwd = os.getcwd()

import_file = os.path.join(cwd, 'BBa_I11031.gb')
output_file = os.path.join(cwd, 'BBa_I11031.dna')

data = {"request": "importDNAFile",
        "inputFile": import_file,
        "outputFile": output_file}

r = requests.post(post_url,params = data,  headers = {"Accept":"text/plain"})
print(r.status_code)
  