#!/usr/bin/env python

"""
Clase que define el stilo de los plots
"""
import ROOT

#jl TStyle
njStyle = ROOT.TStyle('njStyle', "N-J Style");

#set the background color to white
njStyle.SetFillColor(10);
njStyle.SetFrameFillColor(10);
njStyle.SetCanvasColor(10);
njStyle.SetPadColor(10);
njStyle.SetTitleFillColor(0);
njStyle.SetStatColor(10);

#dont put a colored frame around the plots
njStyle.SetFrameBorderMode(0);
njStyle.SetCanvasBorderMode(0);
njStyle.SetPadBorderMode(0);
njStyle.SetLegendBorderSize(0);

#use the primary color palette
njStyle.SetPalette(1);

#set the default line color for a histogram to be black
njStyle.SetHistLineColor(ROOT.kBlack);

#set the default line color for a fit function to be red
njStyle.SetFuncColor(ROOT.kRed);

#make the axis labels black
njStyle.SetLabelColor(ROOT.kBlack,"xyz");

#set the default title color to be black
njStyle.SetTitleColor(ROOT.kBlack)
 
#set the margins
njStyle.SetPadBottomMargin(0.1)
njStyle.SetPadTopMargin(0.08)
njStyle.SetPadRightMargin(0.1)
#njStyle.SetPadLeftMargin(0.17);
njStyle.SetPadLeftMargin(0.12);

#set axis label and title text sizes
njStyle.SetLabelFont(42,"xyz")
njStyle.SetLabelSize(0.04,"xyz")
njStyle.SetLabelOffset(0.015,"xyz")
njStyle.SetTitleFont(42,"xyz")
njStyle.SetTitleSize(0.05,"xyz")
njStyle.SetTitleOffset(1.1,"yz")
njStyle.SetTitleOffset(1.0,"x")
njStyle.SetStatFont(42);
njStyle.SetStatFontSize(0.05);
njStyle.SetTitleBorderSize(0);
njStyle.SetStatBorderSize(0);
njStyle.SetTextFont(42);

#set line widths
njStyle.SetFrameLineWidth(2);
njStyle.SetFuncWidth(2);
njStyle.SetHistLineWidth(2);

#set the number of divisions to show
njStyle.SetNdivisions(506, "xy");

#turn off xy grids
njStyle.SetPadGridX(0);
njStyle.SetPadGridY(0);

#set the tick mark style
njStyle.SetPadTickX(1);
njStyle.SetPadTickY(1);

#turn off stats
njStyle.SetOptStat(0);
njStyle.SetOptFit(0);

#marker settings
njStyle.SetMarkerStyle(20);
njStyle.SetMarkerSize(0.7);
njStyle.SetLineWidth(2); 

#done
njStyle.cd();
ROOT.gROOT.ForceStyle();
ROOT.gStyle.ls();

