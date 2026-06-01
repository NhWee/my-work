import FWCore.ParameterSet.Config as cms


process = cms.Process("HIJET")

process.maxEvents = cms.untracked.PSet(
    input=cms.untracked.int32(1),
)

process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring(
        "root://eospublic.cern.ch//eos/opendata/cms/hidata/HIRun2011/HIHighPt/RECO/15Apr2013-v1/10000/0056B4D7-E8A5-E211-935E-003048F316C4.root",
    ),
)

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1

process.TFileService = cms.Service(
    "TFileService",
    fileName=cms.string("hihighpt_jets.root"),
)

process.hiJets = cms.EDAnalyzer(
    "HiJetAnalyzer",
    jets=cms.InputTag("ak5PFJets", "", "ppRECO"),
    maxAbsEta=cms.double(2.0),
    minJetPt=cms.double(30.0),
)

process.path = cms.Path(process.hiJets)
