#!/usr/bin/env python

"""clean_silva.py: creates a custom-made version of SILVA's 132 taxonomy DB for Archaea and Bacteria
"""

import argparse
import csv
import re

keywords = set([
";metagenome", ";uncultured", ";Uncultured", ";unidentified", ";enrichment", "_environmental_sample", ";clone",
";environmental_clone", "_culture_clone", "_clone", ";bacterium", ";Terrestrial", ";terrestrial", ";seawater", ";groundwater", 
";marine", ";low_G", ";blackwater", ";freshwater", ";saltmarsh", ";hyperthermophilic", ";iron-reducing", ";Acidobacterium",
";NC10_bacterium", ";drinking_water",  ";uncultivated", ";bioreactor", ";eubacterium", ";synthetic",
";2,4-D-degrading_bacterium", ";Acetothermia_bacterium", ";Acidobacteria_bacterium", ";Actinobacteria_bacterium",
";Aerophobetes_bacterium", ";agricultural_soil", ";alkaliphilic_bacterium", ";Alphaproteobacteria_bacterium",
";Aminicenantes_bacterium", ";ammonia-oxidizing_bacterium", ";anaerobic_", ";aniline-degrading_bacterium",
";Antarctic_", ";Arctic_", ";Armatimonadetes_bacterium", ";arsenic-oxid", ";arsenic_resistant", ";arsenite-oxid",
";Atribacteria_bacterium", ";Bacilli_bacterium", ";Bacterium_BAB", ";Bacteroidetes_bacterium", ";Bacteroidia_bacterium",
";benzo", ";Berkelbacteria_bacterium", ";Betaproteobacteria_bacterium",";drinking_water", ";BTEX",
";biphenthrin-degrading_bacterium", ";biphenyl-degrading_bacterium", ";blackwater_", ";blood_disease", ";bromate-reducing_bacterium",
";butyrate-producing_bacterium", ";Calditrichaeota_bacterium", ";Calescamantes_bacterium", ";Campylobacter_mucosalis-like",
";candidate_division", ";carbazole-degrading_bacterium", ";carrageenase-producing_bacterium", ";Catanema_sp.",";CFB_group",
";chironomid_egg", ";Chlamydiae_bacterium", ";Chlorobi_bacterium", ";Chloroflexi_bacterium", ";cilia-associated_respiratory",
";Citrus_greening", ";Cloacimonetes_bacterium", ";Clostridia_bacterium", ";Corynebacterium-like_bacterium", ";zeta_proteobacterium",
";coryneform_bacterium", ";Croceitalea_bacterium", ";Cyanobacteria/Melainabacteria_group", ";Cytophaga-like_bacterium",
";Daphnia_endosymbiotic", ";Deferribacteres_bacterium", ";Dehalococcoidia_bacterium", ";dehydroabietic_acid-degrading",
";Deltaproteobacteria_bacterium", ";denitrifying_", ";nitrifying", ";dibenzo", ";dissimilatory_selenate-respiring",
";DSMP-degrading_bacterium", ";Elusimicrobia_bacterium", ";endophyte_bacterium", ";endophytic_bacterium", ";Bacteriodetes_bacterium",
";estrogen-degrading_bacterium", ";Eubostrichus_topiarius", ";Fe-oxidizing_bacterium", ";Fibrobacteria_bacterium", ";filamentous_",
";Firmicutes_", ";Flavobacteria_bacterium", ";Flavobacteriia_bacterium", ";Flexibacter_group", ";freshwater_bacterium",
";Gammaproteobacteria_bacterium", ";Gemmatimonadetes_bacterium", ";glacial_ice", ";Glacier_bacterium", ";glacier_",
";Gracilibacteria_bacterium", ";Gram-", ";groundwater_", ";gut_", ";haloalkaliphilic_bacterium", ";halophilic",
";halotolerant_bacterium", ";human_", ";Hydrogenedentes_bacterium", ";hyperthermophilic_bacterium", ";Ignavibacteria_bacterium",
";iodide-oxidizing_bacterium", ";Iron_sulfide-containing", ";jellyfish", ";Kartchner_Caverns", ";proteobacterium",
";Kineococcus-like_bacterium", ";lactic_acid", ";Latescibacteria_bacterium", ";Laxus_cosmopolitus", ";Lentisphaerae_bacterium",
";lobster_gut", ";magneto-ovoid_bacterium", ";marine_", ";Marinimicrobia_bacterium", ";methano",
";methylotrophic_bacterium", ";Microgenomates_", ";mixed_culture", ";mixotrophic_iron-oxidizing", ";monochloroacetic-acid-degrading_bacterium", 
";mucus_bacterium", ";naphthalene-utilizing_bacterium", ";NC10_bacterium", ";nitrogen-fixing_bacterium", ";Nitrospinae_bacterium",
";Nitrospira_bacterium",";Nitrospirae_bacterium", ";North_Sea", ";obligately_oligotrophic", ";oilfield_bacterium", ";OM182_bacterium",
";Omnitrophica_bacterium", ";Omnitrophica_WOR", ";Opitutae_bacterium", ";Parcubacteria_bacterium", ";P-decomposing_bacterium",
";perchlorate-reducing_bacterium", ";phenanthrene-degrading_bacterium", ";phenol-degrading_bacterium", ";phototrophic_bacterium",
";Phycisphaerae_bacterium",";Planctomycetes_bacterium", ";Planctomycetia_bacterium", ";planktonic_bacterium", ";polar_sea",";poultry_manure",
";Proteobacteria_bacterium", ";psychrophilic_", ";PVC_group", ";rainbow_trout", ";rape_rhizosphere", ";Raricirrus_beryli", ";Rasbo_bacterium",
";Red_Sea", ";rhizosphere_bacterium", ";Rhodobacter_group", ";Robbea_sp.", ";rumen_bacterium", ";ruminal_bacterium", ";SAR11_cluster",
";SAR202_cluster", ";SAR324_cluster", ";SAR86_cluster", ";SAR92_bacterium", ";sediment_", ";selenate-reducing_bacterium",
";Siboglinum_sp.", ";simazine-degrading_bacterium", ";soil_", ";Spartobacteria_bacterium", ";Sphingobacteriia_bacterium",
";Sphingomonas-like_bacterium", ";Spirochaetes_bacterium", ";sponge_bacterium", ";SR1_bacterium",";Stilbonema_sp.", ";Bacteriodetes",
";subglacial_outflow", ";sulfate-reducing_bacterium", ";sulfidic_hot", ";sulfur-", ";Sulfur", ";swine_", ";Synergistetes_bacterium",
";Tenericutes_bacterium", ";thermal_soil", ";thermophilic_", ";Tissierellia_bacterium", ";TM7_bacterium", ";toluene-degrading_methanogenic",  
";triclosan-degrading_bacterium", ";type_I", ";Verrucomicrobia_bacterium", ";Verrucomicrobiae_bacterium", ";Xanthomonas_group",
";Zetaproteobacteria_bacterium", ";alpha_proteobacterium", ";beta", ";BEV_proteobacterium_", ";delta_proteobacterium",
";epsilon_proteobacterium", ";Folliculinopsis_sp._SKG-2010a", ";gamma_proteobacterium", ";magnetic_proteobacterium_strain",";marine_", 
";methylotrophic", ";Olavius_", ";SAR116_cluster_alpha", ";SBR_proteobacterium_", ";SMC_proteobacterium_", ";unknown_marine_alpha",
";symbiont", ";endosymbi", ";spirochete", ";midgut", ";primary", ";secondary", "_enrichment", ";actino", "_oral_", ";oral", ";hot_",
";haloarchaeon", ";archaeon", "_archaeon", ";hydrocarbon_", ";wastewater", ";permafrost", ";compost_", "_canine_", ";korarchaeote",
";Bacteroidetes_sp", "Flavobacterium-like", ";unclassified", ";Sphingobacterium-like", "bacter;Flavobacterium", ";epibiont", ";Alviniconcha",
";artificial", ";anammox", ";anoxic", ";planctomycete", ";star", ";gas", ";Phage", ";diazotroph", ";humic", ";food", ";mollusc", ";deep", ";rod-"
])


isproblem = re.compile(";arsenic_resistant|water|;Raricirrus_beryli|;filamentous_|_bacterium|;bacterium|;rape_rhizosphere|;SAR116_cluster_alpha|;secondary|;rainbow_trout|;SAR202_cluster|;glacier_|methanogenic|_proteobacterium|;proteobacterium|clone|;swine_|;subglacial_outflow|_group|;midgut|rctic|endosymbio|;Eubostrichus_topiarius|;type_I|;Catanema_sp.|;cilia-associated_respiratory|;low_G|;denitrifying_|;unidentified|;SAR86_cluster|;Laxus_cosmopolitus|;SAR324_cluster|;human_|;Iron_sulfide-containing|;mixed_culture|;glacial_ice|;Robbea_sp.|;Bacterium_BAB|;sulfidic_hot|;marine|;Microgenomates_|;Citrus_greening|;Gram-|;halophilic_|_Sea|;Parcubacteria_|errestrial|;candidate_division|;iron-reducing|;Kartchner_Caverns|;blood_disease|-like|;methylotrophic_;Siboglinum_sp.|metagenome|;Omnitrophica_WOR|;psychrophilic_|;spirochete|;poultry_manure|;Folliculinopsis_sp._SKG-2010a|_sea|-sea|;hyperthermophilic|_environmental_sample|;dissimilatory_selenate-respiring|;saltmarsh|;methanotrophic_|;Stilbonema_sp.|biont|;enrichment|;mixotrophic_iron-oxidizing|;arsenite-oxid|;unknown_marine_alpha|;primary|;lactic_acid|soil|;SAR11_cluster|;dehydroabietic_acid-degrading|;thermophilic_|;chironomid_egg|;arsenic-oxid|;lobster_gut|;anaerobic_|cultured|;obligately_oligotrophic|;uncultivated|sp\.|;actino|str\.|pv\.|;gut|archaeo|cf\.|aff\.|_gen|;eubacterium|;synthetic|Bacteriodetes|unclassified|;artificial|;planctomycete|;gas|;Phage|;beta|;humic")


def writetab(tab, handle):
	out = open(handle, "w")
	for(key, value) in tab.iteritems():
		line = key+"\t"+value+"\n"
		out.write(line)

def cleantab(tab, aux):
	output = dict()
	with open(tab) as csvfile:
		reader = csv.reader(csvfile, delimiter="\t")
		for row in reader:
			ID = row[0]
			tax = row[1]
			#print(tax)
			prok = re.search("^Archaea;|^Bacteria;", tax)
			if(prok != None):
				if(tax in aux):
					tax = aux[tax]
				else:
					tax = tax.replace("'", "")
					tax = tax.replace("]", "")
					tax = tax.replace("[", "")
					#print(tax)
					##First search for very frequently misasigned clades
					search = re.search("((Lactob|B)acillus|Streptococcus)_", tax)
					if(search != None):
						search = re.search("Bacilli", tax)
						if(search == None):
							tax = ";".join(tax.split(";")[0:6])
					else:
						search = re.search("(Vibrio_)", tax)
						if(search != None):
							search = re.search("Vibrionales", tax)
							if(search == None):
								tax = ";".join(tax.split(";")[0:6])
						else:
							search = re.search("(Clostridium_)", tax)
							if(search != None):
								search = re.search("Clostridiales", tax)
								if(search == None):
									tax = ";".join(tax.split(";")[0:6])
							else:
								search = re.search("(Mycobacterium_)", tax)
								if(search != None):
									search = re.search("Corynebacteriales", tax)
									if(search == None):
										tax = ";".join(tax.split(";")[0:6])
								else:
									search = re.search("(Pseudomonas_)", tax)
									if(search != None):
										search = re.search("Pseudomonadales", tax)
										if(search == None):
											tax = ";".join(tax.split(";")[0:6])
					#print(tax)
					prob = re.search(isproblem, tax)
					if(prob != None):
						for item in keywords:
							search = re.search(item, tax)
							if(search != None):
								tax = tax.split(item)[0]
						#print("Got a problem")
						marker=re.compile(";[A-Z][a-z]+(eae|ales|proteobacteria)_(str|sp|pv|subsp|genomosp|gen)\.")
						prob = re.search(marker, tax)
						if(prob != None):
							tax = ";".join(tax.split(";")[0:6])
						else:
							marker=re.compile(";[A-Z][a-z]+(eae|ales|proteobacteria|archaeota)_(bacterium|archaeon)")
							prob = re.search(marker, tax)
							if(prob != None):
								tax = ";".join(tax.split(";")[0:6])
							else:
								tax = re.sub("(_subsp\._|_genomosp\._|_sp\._|_str\._|_pv\._|_aff\._|cf\._|_gen\._)", ";", tax)
								tax = re.sub("_sp\.", ";", tax)
					search = re.search("Candidatus_[A-Za-z]+_[A-Za-z]+_", tax)
					if(search != None):
						tax=re.sub("Candidatus_[A-Za-z]+_[A-Za-z]+(_)", ";", tax)
					else:
						search = re.search(";[A-Za-z]+_[A-Za-z]+_", tax)
						if(search != None):
							tax=re.sub("[A-Za-z]+_[A-Za-z]+(_)", ";", tax)
					#print(tax)
				tax = tax.split(";;")[0]
			output[ID] = tax
	return(output)
					

def readaux(tab):
	replace = dict()
	with open(tab) as csvfile:
		reader = csv.reader(csvfile, delimiter="\t")
		for row in reader:
			replace[row[0]] = row[1]
	return(replace)


def main(intable, auxtable, outtable):
	replacements = readaux(auxtable)
	newtab = cleantab(intable, replacements)
	writetab(newtab, outtable)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Creates a manually curated version of the SILVA 132 taxonomy')
	parser.add_argument('-i', '--intable', help='TSV table with id:s on the first column and taxonomy on the right')
	parser.add_argument('-a', '--auxtable', help='Table with particular taxa that need to be trimmed')
	parser.add_argument('-o', '--outtable', help='Output table with id:s on the first column and curated taxonomy on the right')

	args = parser.parse_args()
	
	main(args.intable, args.auxtable, args.outtable)
