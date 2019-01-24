#!/usr/bin/env Rscript

library("optparse")

read_table<-function(filehandle, keep_sample){
    raw<-read.table(filehandle, header=TRUE, row.names=1)
    data<-raw[,1:(ncol(raw)-2)]
    sums<-apply(data, 2, sum)
    keep<-which(sums>keep_sample)
    data<-data[,keep]
    return(data)
}

read_sims<-function(filehandle){
    simtab<-read.table(filehandle)[,1:3]
    colnames(simtab)<-c("OTU1", "OTU2", "Similarity")
    simtab[,1]<-as.character(simtab[,1])
    simtab[,2]<-as.character(simtab[,2])
    simtab[,3]<-as.numeric(simtab[,3])
    simtab<-as.data.frame(simtab)
    return(simtab)
}


flag_otu<-function(sim, counts, abund_weak, abund_strong, id_weak, id_strong){
   
 
    all_otu <- unique(c(simtab$OTU1, simtab$OTU2))
    analyse <- intersect(all_otu, rownames(counts))

    artefacts<-matrix(0, nrow=nrow(counts), ncol=2)
    rownames(artefacts)<-rownames(counts)
    colnames(artefacts)<-c("Weak", "Strong")

    flagged<-c()
    
    rowsum<-apply(counts, 1, sum)

    strong<-which(simtab$Similarity >= id_strong)

    for(index in strong){
        otu1<-simtab$OTU1[index]
        otu2<-simtab$OTU2[index]
        if(otu1 %in% analyse & otu2 %in% analyse){
            sum1<-rowsum[which(names(rowsum)==otu1)]
            sum2<-rowsum[which(names(rowsum)==otu2)]
            if(sum1>0 & sum2>0){
                if(sum1 > sum2 & !is.element(otu2, flagged)){
                    ratio<-sum1/sum2
                    pos<-grep(otu2, rownames(artefacts))
                    if(ratio >= abund_strong){
                        artefacts[pos, 2]<-1
                        flagged<-c(flagged, otu2)
                    }
                    else if(ratio >= abund_weak){
                        artefacts[pos, 1]<-1
                    }
                }
                else if (!is.element(otu1, flagged)){
                    ratio<-sum2/sum1
                    pos<-grep(otu1, rownames(artefacts))
                    if(ratio >= abund_strong){
                        artefacts[pos, 2]<-1
                        flagged<-c(flagged, otu1)
                    }
                    else if(ratio >= abund_weak){
                        artefacts[pos, 1]<-1
                    }
                }
            }
        }
    }

    weak<-which(simtab$Similarity >= id_weak & simtab$Similarity < id_strong)
    for(index in weak){
        otu1<-simtab$OTU1[index]
        otu2<-simtab$OTU2[index]
        if(otu1 %in% analyse & otu2 %in% analyse){
            sum1<-rowsum[which(names(rowsum)==otu1)]
            sum2<-rowsum[which(names(rowsum)==otu2)]
            if(sum1>0 & sum2>0){
               if(sum1 > sum2 & !is.element(otu2, flagged)){
                    ratio<-sum1/sum2
                    pos<-grep(otu2, rownames(artefacts))
                    if(ratio >= abund_weak){
                        artefacts[pos, 1]<-1
                        flagged<-c(flagged, otu2)
                    }
                }
                else if (!is.element(otu1, flagged)){
                    ratio<-sum2/sum1
                    pos<-grep(otu1, rownames(artefacts))
                    if(ratio >= abund_weak){
                        artefacts[pos, 1]<-1
                        flagged<-c(flagged, otu1)
                    }
                }
            }
        }
    }

    flags<-rep("C", times=nrow(artefacts))
    flags[which(artefacts[,1]==1)]<-"W"
    flags[which(artefacts[,2]==1)]<-"S"
    
     return(list(flags=flags, sums=rowsum))
}

make_bars<-function(flags, sums){

    maxrow<-max(sums)
    bins<-c(0)
    lim<-1
    while(lim<maxrow){
        bins<-c(bins, lim)
        lim<-lim*2
    }
    bins<-c(bins, maxrow)

    bars<-matrix(nrow=length(bins), ncol=3)
    rownames(bars)<-bins[1:length(bins)]
    colnames(bars)=c("Confident", "Weak artefact", "Strong artefact")
    for(i in 1:length(bins)){
        min<-bins[i]
        max<-bins[i+1]
        clean<-which(sums>min & sums<=max & flags=="C")
        weak<-which(sums>min & sums<=max & flags=="W")
        strong<-which(sums>min & sums<=max & flags=="S")
        bars[i, ]<-c(length(clean), length(weak), length(strong))
    }
    bars<-t(bars[2:nrow(bars),])
    return(bars)
}


print_bars<-function(bars, title = "Octave Plot", filehandle){
	pdf(filehandle)
	barplot(bars, las=2, col=c("cornflowerblue", "lightgoldenrod", "salmon"), legend=TRUE,
       		ylab = "OTU counts", xlab = "OTU abundance")
	title(title)
	dev.off()
}


option_list <- list(
	make_option("--otutab", help="TSV table, OTU in rows and samples in columns, annotation on the last 2 columns", type="character"),
	make_option("--simtab", help="Blast 6-format table of pairwise comparisons between centroids", type="character"),
	make_option("--A_weak", default=32, help="Abundance ratio for flagging Weak; default = 32", type="double"),
        make_option("--A_strong", default=256, help="Abundance ratio for flagging Strong; default = 256", type="double"),
	make_option("--ID_weak", default=97, help="% sequence identity for flagging Weak; default 97", type="double"),
        make_option("--ID_strong", default=99, help="% sequence identity  for flagging Strong; default 99", type="double"),
	make_option("--sample_size", default=1000, help="Discard samples with fewer reads than this; default 1000", type="character"),
	make_option("--title", default="Octave plot", help="Plot title", type="character"),
	make_option("--outfile", default="octave.pdf", help="path to output pdf file", type="character")
	)
args<-parse_args2(OptionParser(option_list = option_list))

otu_tab<-read_table(args$options$otutab, args$options$sample_size)
simtab<-read_sims(args$options$simtab)
prep<-flag_otu(counts=otu_tab, sim=simtab, 
	abund_weak = args$options$A_weak, abund_strong = args$options$A_strong, id_weak = args$options$ID_weak, id_strong = args$options$ID_strong)
bars<-make_bars(flags = prep$flags, sum = prep$sums)
print_bars(bars, args$options$title, args$options$outfile)


