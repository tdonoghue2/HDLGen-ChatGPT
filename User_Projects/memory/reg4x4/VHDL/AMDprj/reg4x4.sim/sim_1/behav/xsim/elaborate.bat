@echo off
REM ****************************************************************************
REM Vivado (TM) v2019.1 (64-bit)
REM
REM Filename    : elaborate.bat
REM Simulator   : Xilinx Vivado Simulator
REM Description : Script for elaborating the compiled design
REM
REM Generated by Vivado on Sun Apr 02 10:47:19 +0100 2023
REM SW Build 2552052 on Fri May 24 14:49:42 MDT 2019
REM
REM Copyright 1986-2019 Xilinx, Inc. All Rights Reserved.
REM
REM usage: elaborate.bat
REM
REM ****************************************************************************
echo "xelab -wto a0d826938b39464a877dd6e891cecbe0 --incr --debug typical --relax --mt 2 -L xil_defaultlib -L secureip --snapshot reg4x4_TB_behav xil_defaultlib.reg4x4_TB -log elaborate.log"
call xelab  -wto a0d826938b39464a877dd6e891cecbe0 --incr --debug typical --relax --mt 2 -L xil_defaultlib -L secureip --snapshot reg4x4_TB_behav xil_defaultlib.reg4x4_TB -log elaborate.log
if "%errorlevel%"=="0" goto SUCCESS
if "%errorlevel%"=="1" goto END
:END
exit 1
:SUCCESS
exit 0