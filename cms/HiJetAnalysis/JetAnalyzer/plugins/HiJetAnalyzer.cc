#include <cmath>
#include <vector>

#include "TTree.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/Common/interface/View.h"
#include "DataFormats/HeavyIonEvent/interface/Centrality.h"
#include "DataFormats/JetReco/interface/Jet.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

class HiJetAnalyzer : public edm::EDAnalyzer {
public:
  explicit HiJetAnalyzer(const edm::ParameterSet& config);
  ~HiJetAnalyzer() {}

private:
  virtual void analyze(const edm::Event& event, const edm::EventSetup& setup);

  edm::InputTag jets_;
  edm::InputTag centrality_;
  double maxAbsEta_;
  double minJetPt_;

  TTree* tree_;
  unsigned int run_;
  unsigned int lumi_;
  unsigned long long event_;
  float centralityRaw_;
  float hfTowerSum_;
  int nJet_;
  float leadPt_;
  float leadEta_;
  float leadPhi_;
  float subleadPt_;
  float subleadEta_;
  float subleadPhi_;
  float dphi_;
  float aj_;
  std::vector<float> jetPt_;
  std::vector<float> jetEta_;
  std::vector<float> jetPhi_;
};

HiJetAnalyzer::HiJetAnalyzer(const edm::ParameterSet& config)
    : jets_(config.getParameter<edm::InputTag>("jets")),
      centrality_(config.getParameter<edm::InputTag>("centrality")),
      maxAbsEta_(config.getParameter<double>("maxAbsEta")),
      minJetPt_(config.getParameter<double>("minJetPt")),
      tree_(0),
      run_(0),
      lumi_(0),
      event_(0),
      centralityRaw_(-1.0),
      hfTowerSum_(-1.0),
      nJet_(0),
      leadPt_(-1.0),
      leadEta_(0.0),
      leadPhi_(0.0),
      subleadPt_(-1.0),
      subleadEta_(0.0),
      subleadPhi_(0.0),
      dphi_(-1.0),
      aj_(-1.0),
      jetPt_(),
      jetEta_(),
      jetPhi_() {
  edm::Service<TFileService> fileService;
  tree_ = fileService->make<TTree>("jets", "Leading and subleading jet summary");
  tree_->Branch("run", &run_, "run/i");
  tree_->Branch("lumi", &lumi_, "lumi/i");
  tree_->Branch("event", &event_, "event/l");
  tree_->Branch("centrality_raw", &centralityRaw_, "centrality_raw/F");
  tree_->Branch("hf_tower_sum", &hfTowerSum_, "hf_tower_sum/F");
  tree_->Branch("nJet", &nJet_, "nJet/I");
  tree_->Branch("lead_pt", &leadPt_, "lead_pt/F");
  tree_->Branch("lead_eta", &leadEta_, "lead_eta/F");
  tree_->Branch("lead_phi", &leadPhi_, "lead_phi/F");
  tree_->Branch("sublead_pt", &subleadPt_, "sublead_pt/F");
  tree_->Branch("sublead_eta", &subleadEta_, "sublead_eta/F");
  tree_->Branch("sublead_phi", &subleadPhi_, "sublead_phi/F");
  tree_->Branch("dphi", &dphi_, "dphi/F");
  tree_->Branch("aj", &aj_, "aj/F");
  tree_->Branch("jet_pt", &jetPt_);
  tree_->Branch("jet_eta", &jetEta_);
  tree_->Branch("jet_phi", &jetPhi_);
}

void HiJetAnalyzer::analyze(const edm::Event& event, const edm::EventSetup&) {
  run_ = event.id().run();
  lumi_ = event.luminosityBlock();
  event_ = event.id().event();
  centralityRaw_ = -1.0;
  hfTowerSum_ = -1.0;
  nJet_ = 0;
  leadPt_ = -1.0;
  leadEta_ = 0.0;
  leadPhi_ = 0.0;
  subleadPt_ = -1.0;
  subleadEta_ = 0.0;
  subleadPhi_ = 0.0;
  dphi_ = -1.0;
  aj_ = -1.0;
  jetPt_.clear();
  jetEta_.clear();
  jetPhi_.clear();

  edm::Handle<reco::Centrality> centrality;
  event.getByLabel(centrality_, centrality);
  if (centrality.isValid()) {
    centralityRaw_ = centrality->raw();
    hfTowerSum_ = centrality->EtHFtowerSum();
  }

  edm::Handle<edm::View<reco::Jet> > jets;
  event.getByLabel(jets_, jets);

  for (edm::View<reco::Jet>::const_iterator jet = jets->begin(); jet != jets->end(); ++jet) {
    if (jet->pt() < minJetPt_) {
      continue;
    }
    if (std::fabs(jet->eta()) > maxAbsEta_) {
      continue;
    }

    ++nJet_;
    jetPt_.push_back(jet->pt());
    jetEta_.push_back(jet->eta());
    jetPhi_.push_back(jet->phi());

    if (jet->pt() > leadPt_) {
      subleadPt_ = leadPt_;
      subleadEta_ = leadEta_;
      subleadPhi_ = leadPhi_;
      leadPt_ = jet->pt();
      leadEta_ = jet->eta();
      leadPhi_ = jet->phi();
    } else if (jet->pt() > subleadPt_) {
      subleadPt_ = jet->pt();
      subleadEta_ = jet->eta();
      subleadPhi_ = jet->phi();
    }
  }

  if (leadPt_ > 0.0 && subleadPt_ > 0.0) {
    dphi_ = std::fabs(leadPhi_ - subleadPhi_);
    while (dphi_ > M_PI) {
      dphi_ = std::fabs(dphi_ - 2.0 * M_PI);
    }
    aj_ = (leadPt_ - subleadPt_) / (leadPt_ + subleadPt_);
  }

  tree_->Fill();
}

DEFINE_FWK_MODULE(HiJetAnalyzer);
