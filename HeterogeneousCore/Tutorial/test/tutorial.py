import FWCore.ParameterSet.Config as cms

# use the Phase-2 era corresponding to the D128 geometry
from Configuration.Eras.Era_Phase2C26I13M9_cff import Phase2C26I13M9
process = cms.Process("TUTORIAL", Phase2C26I13M9)

# enable multithreading
process.options.numberOfThreads = 8
process.options.numberOfStreams = 0

# enable alpaka and GPU support
process.load("Configuration.StandardSequences.Accelerators_cff")

# run over recent RelVal samples
from IOPool.Input.modules import PoolSource
process.source = PoolSource(
    fileNames = [
        # dasgoclient --query 'file dataset=/RelValTTbar_14TeV/CMSSW_20_1_0_pre3-PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/GEN-SIM-DIGI-RAW' | head
        "/store/relval/CMSSW_20_1_0_pre3/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/2830000/fc29a6bd-b4bc-4038-9c49-d44eb9724992.root",
        "/store/relval/CMSSW_20_1_0_pre3/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/2830000/653dcc08-10c5-497e-8394-f31096868d42.root",
        "/store/relval/CMSSW_20_1_0_pre3/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/2830000/f454bd04-4109-4514-a91f-751205450ceb.root",
        "/store/relval/CMSSW_20_1_0_pre3/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/2830000/0ad010d4-030c-42ac-9ce9-9fb8c81fc1e2.root",
        "/store/relval/CMSSW_20_1_0_pre3/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/2830000/2be2503a-df34-4c1d-ae58-d9ca27173364.root",
        "/store/relval/CMSSW_20_1_0_pre3/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/2830000/bc46955d-4ad6-4cc2-9848-e11a6cff6252.root",
        "/store/relval/CMSSW_20_1_0_pre3/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/2830000/88fb9d38-3cab-4bb5-b7d9-ff79931ebe51.root",
        "/store/relval/CMSSW_20_1_0_pre3/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/2830000/9c7e1073-feb2-4545-98a9-a1d8dcae1075.root",
        "/store/relval/CMSSW_20_1_0_pre3/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/2830000/698a0144-1fa6-4637-9c2d-e48df395f1c6.root",
        "/store/relval/CMSSW_20_1_0_pre3/RelValTTbar_14TeV/GEN-SIM-DIGI-RAW/PU_150X_mcRun4_realistic_v1_STD_D128_RegeneratedGS_PU_20260903_192421_RV19-v1/2830000/2c3bcfee-f87b-4bf0-8c8f-af5c5b08b261.root",
    ])

# process only 1000 events
process.maxEvents.input = 100

# print a message every event
process.MessageLogger.cerr.FwkReport.reportEvery = 1

# do not print the time and trigger reports at the end of the job
process.options.wantSummary = False

# load the Phase-2 D128 geometry
process.load("Configuration.Geometry.GeometryExtendedRun4D128Reco_cff")

# configure the global tag for the D128 geometry (150X_mcRun4_realistic_v1 with the T35 tracker conditions)
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(None, globaltag = 'auto:phase2_realistic_T35')

# import the definition of the Tutorial modules
from HeterogeneousCore.Tutorial.modules import *

# convert PFJets to SoA format
process.pfJetsSoA = tutorial_PFJetsSoAProducer_alpaka(
    jets = "hltAK4PFJetsCorrected"
)

# or, use the underlying syntax
# process.pfJetsSoA = cms.EDProducer('tutorial::PFJetsSoAProducer@alpaka',
#     jets = cms.InputTag("hltAK4PFJetsCorrected")
# )

# produce the corrections in the EventSetup
from FWCore.Modules.modules import EmptyESSource
process.SoACorrectorRecord = EmptyESSource(
    recordName = "tutorial::SoACorrectorRecord",
    firstValid = 1
)

process.SoACorrectorESProducer = tutorial_SoACorrectorESProducer_alpaka()

# apply the corrections
process.pfJetsSoACorrected = tutorial_PFJetsSoACorrector_alpaka(
    jets = "pfJetsSoA"
)

# select pairs and triplets of corrected jets with an invariant mass within the given range
process.invariantMassSelector = tutorial_InvariantMassSelector_alpaka(
    jets = "pfJetsSoACorrected",
    pT_min = 20.,    # GeV
    pT_max = 300.,   # GeV
    eta_min = 0.,
    eta_max = 3.,
    mass_min = 75.,  # GeV
    mass_max = 105., # GeV
)
process.MessageLogger.cerr.InvariantMassSelector = cms.untracked.PSet()

# dump the PF jets and SoA jets
process.pfJetsSoAAnalyzer = tutorial_PFJetsSoAAnalyzer(
    jets = "hltAK4PFJetsCorrected",
    soa = "pfJetsSoACorrected",
    ntuplets = "invariantMassSelector"
)
process.MessageLogger.cerr.PFJetsSoAAnalyzer = cms.untracked.PSet()

# schedule the modules
process.path = cms.Path(
    process.pfJetsSoA +
    process.pfJetsSoACorrected +
    process.invariantMassSelector +
    process.pfJetsSoAAnalyzer
)

process.schedule = cms.Schedule(
    process.path
)
