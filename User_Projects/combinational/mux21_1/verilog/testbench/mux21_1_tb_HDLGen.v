/* 
VHDL testbench mux21_1_TB
Generated by HDLGen, Github https://github.com/abishek-bupathi/HDLGen
Reference: https://tinyurl.com/VHDLTips

Component Name : mux21_1
Title          : 2-to-1 mux, 1-bit data
Description    : refer to component hdl model for function description and signal dictionary
Author(s)      : Fearghal Morgan
Company        : University of Galway
Email          : fearghal.morgan@universityofgalway.ie
Date           : 31/03/2023
*/

// FM no library section

// module declaration. No inputs or outputs
module mux21_1_TB();

// testbench signal declarations
integer testNo; // aids locating test in simulation waveform
reg endOfSim;   // assert at end of simulation to highlight simulation done. Stops clk signal generation.

// <FM  update text> Typically use the same signal names as in the Verilog module, with keyword reg added for module inputs and keyword wire added for module outputs
reg sel;
reg muxIn1;
reg muxIn0;
wire muxOut;

parameter  period = 20; // 20 ns
initial endOfSim = 1'b0;

// No begin in verilog
 
// instantiate unit under test (UUT)
mux21_1 uut
(
		.sel (sel),
		.muxIn1 (muxIn1),
		.muxIn0 (muxIn0),
		.muxOut (muxOut)
	);

initial
begin
 $timeformat(-9, 2, " ns", 20);
 $display("Simulation start :: time is %0t",$time);
 
/* Apply default INPUT signal values. Do not assign output signals (generated by the UUT) here
*/
 testNo = 0;
 sel = 1'b0;
 muxIn1 = 1'b0;
 muxIn0 = 1'b0;
 #period

 // Include testbench stimulus sequence here, i.e, input signal combinations 
 // manually added code START
    // include testbench stimulus sequence here. Use new testNo for each test set
    // individual tests. Generate input signal combinations and 
	// repeat(number of times) 
	//  #period
    testNo <= 1;
	repeat(2) 
	 #period
 // manually added code END

 // Print picosecond (ps) = 1000*ns (nanosecond) time to simulation transcript
 // Use to find time when simulation ends (endOfSim is TRUE)
 // Re-run the simulation for this time 
 // Select timing diagram and use View>Zoom Fit  
 $display("Simulation end :: time is %0t",$time);
 endOfSim = 1'b1; // assert to stop clk signal generation

end 

endmodule