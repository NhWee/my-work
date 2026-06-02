import os

import FWCore.ParameterSet.Config as cms


max_events = int(os.environ.get("MAX_EVENTS", "10"))
output_file = os.environ.get("OUTPUT_FILE", "pp2760_jets.root")
min_jet_pt = float(os.environ.get("MIN_JET_PT", "30.0"))
input_file = os.environ.get(
    "INPUT_FILE",
    "root://eospublic.cern.ch//eos/opendata/cms/Run2011A/AllPhysics2760/RECO/16Jul2011-v1/0000/00135ABC-6AB1-E011-B6C6-00E08178C0F7.root",
)


process = cms.Process("PPJET")

process.maxEvents = cms.untracked.PSet(
    input=cms.untracked.int32(max_events),
)

process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring(
        input_file,
    ),
)

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.TFileService = cms.Service(
    "TFileService",
    fileName=cms.string(output_file),
)

process.hiJets = cms.EDAnalyzer(
    "HiJetAnalyzer",
    jets=cms.InputTag("ak5PFJets", "", "RECO"),
    centrality=cms.InputTag("hiCentrality", "", "RECO"),
    maxAbsEta=cms.double(2.0),
    minJetPt=cms.double(min_jet_pt),
)

process.path = cms.Path(process.hiJets)
