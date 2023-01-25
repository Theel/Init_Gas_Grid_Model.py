within ;
model Test_Bench_Pipe
inner TransiEnt.SimCenter simCenter(
    showExpertSummary=true,
    useHomotopy=true,                                 redeclare TransiEnt.Basics.Media.Gases.VLE_VDIWA_SG4_var gasModel1)                                                                                                                                                                                                         annotation (Placement(transformation(extent={{-70,80},{-50,100}})));
parameter TILMedia.VLEFluidTypes.BaseVLEFluid medium = simCenter.gasModel1 "Medium natural gas mixture";
//-------------------------------------------------------------------------------------------------------------
TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_Txim_flow Sink_at_1(
    p_nom=0,
     m_flow_const=0.35,
    variable_m_flow=true,
    m_flow_nom=0,
    m(start=0.35))    annotation (Placement(transformation(
 extent={{10.372,-10.6277},{-10.372,10.6277}},
 origin={43.628,0.6277})));

  TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_pTxi boundary_pTxi1(p_const=1600000) annotation (Placement(transformation(extent={{-66,-10},{-46,10}})));

 PipeFlow_L4_Advanced pipe_advanced(
     frictionAtInlet=true,
     frictionAtOutlet=true,
    redeclare model PressureLoss = ClaRa.Basics.ControlVolumes.Fundamentals.PressureLoss.Generic_PL.LinearPressureLoss_L4,
    initOption=0,
    useHomotopy=true,
    m_flow_start=ones(pipe.N_cv + 1)*0.3188655001328929,
    showExpertSummary=true,
    showData=true,
    length=5000,
     diameter_i=0.3,
     h_start=TILMedia.Internals.VLEFluidConfigurations.FullyMixtureCompatible.VLEFluidFunctions.specificEnthalpy_pTxi(medium,pipe_advanced.p_start,pipe_advanced.T_start,pipe_advanced.xi_start),
     T_start=ones(pipe_advanced.N_cv)*293.15,
     p_start=linspace(
      1593073.8073222376,
      1600000.0,
      pipe_advanced.N_cv),
    N_cv=3)                                                                                               annotation (Placement(transformation(extent={{-22,-8},{8,8}})));
//-------------------------------------------------------------------------------------------------------------
TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_Txim_flow Sink_at_2(m_flow_const=0.35, variable_m_flow=true)
                      annotation (Placement(transformation(
 extent={{10.372,-10.6277},{-10.372,10.6277}},
 origin={45.628,-39.3723})));
  TransiEnt.Components.Boundaries.Gas.BoundaryRealGas_pTxi boundary_pTxi2(p_const=1600000) annotation (Placement(transformation(extent={{-62,-50},{-42,-30}})));
  TransiEnt.Components.Gas.VolumesValvesFittings.Pipes.PipeFlow_L4_Simple pipe(
    frictionAtInlet=true,
    frictionAtOutlet=true,
    redeclare model PressureLoss = ClaRa.Basics.ControlVolumes.Fundamentals.PressureLoss.VLE_PL.QuadraticNominalPoint_L4,
    m_flow_nom=0.5,
    Delta_p_nom=1100,
    useHomotopy=true,
    showExpertSummary=true,
    showData=true,
    length=5000,
    diameter_i=0.3,
     xi_start=medium.xi_default,
     h_start=TILMedia.Internals.VLEFluidConfigurations.FullyMixtureCompatible.VLEFluidFunctions.specificEnthalpy_pTxi(medium,pipe.p_start,pipe.T_start,pipe.xi_start),
     T_start=ones(pipe.N_cv)*293.15,
     p_start=linspace(
      1593073.8073222376,
      1600000.0,
      pipe.N_cv),
     m_flow_start=ones(pipe.N_cv + 1)*0.3188655001328929)  annotation (Placement(transformation(extent={{-16,-46},{12,-34}})));
//-------------------------------------------------------------------------------------------------------------
  ClaRa.Components.BoundaryConditions.BoundaryGas_pTxi boundaryGas_pTxi(medium=TransiEnt.Basics.Media.Gases.Gas_VDIWA_SG4_var(), p_const(displayUnit="bar") = 1600000)
                                                                                                                                             annotation (Placement(transformation(extent={{-110,18},{-90,38}})));
  ClaRa.Components.BoundaryConditions.BoundaryGas_Txim_flow boundaryGas_Txim_flow(
    medium=TransiEnt.Basics.Media.Gases.Gas_VDIWA_SG4_var(),
    variable_m_flow=true,
    m_flow_const=0.35)                                                                                                                                        annotation (Placement(transformation(extent={{40,18},{20,38}})));
  ClaraPipeGas_L4_Advanced pipe_ClaraAdvanced(
    medium=TransiEnt.Basics.Media.Gases.Gas_VDIWA_SG4_var(),
    use2HeatPorts=false,
    frictionAtInlet=true,
    frictionAtOutlet=true,
    redeclare model PressureLoss = ClaRa.Basics.ControlVolumes.Fundamentals.PressureLoss.Generic_PL.LinearPressureLoss_L4,
    p_nom(displayUnit="Pa"),
    m_flow_nom=0.5,
    Delta_p_nom=1100,
    initOption=0,
    useHomotopy=false,
    length=5000,
    diameter_i=0.3,
    T_start=ones(pipe_ClaraAdvanced.N_cv)*293.15,
    p_start=linspace(
        1593073.8073222376,
        1600000.0,
        pipe_ClaraAdvanced.N_cv),
    m_flow_start=ones(pipe_ClaraAdvanced.N_cv + 1)*0.3188655001328929)  annotation (Placement(transformation(extent={{-58,22},{-26,34}})));
 //-------------------------------------------------------------------------------------------------------------
  ClaRa.Components.BoundaryConditions.BoundaryGas_pTxi boundaryGas_pTxi1(medium=TransiEnt.Basics.Media.Gases.Gas_VDIWA_SG4_var(), p_const(displayUnit="bar") = 1600000)
                                                                                                                                             annotation (Placement(transformation(extent={{-114,44},{-94,64}})));
  ClaRa.Components.BoundaryConditions.BoundaryGas_Txim_flow boundaryGas_Txim_flow1(
    medium=TransiEnt.Basics.Media.Gases.Gas_VDIWA_SG4_var(),
    variable_m_flow=true,
    m_flow_const=0.35) annotation (Placement(transformation(extent={{36,44},{16,64}})));

  ClaRa.Components.VolumesValvesFittings.Pipes.PipeFlowGas_L4_Simple pipe_ClaraSimple(
    medium=TransiEnt.Basics.Media.Gases.Gas_VDIWA_SG4_var(),
    frictionAtInlet=true,
    frictionAtOutlet=true,
    redeclare model PressureLoss = ClaRa.Basics.ControlVolumes.Fundamentals.PressureLoss.Gas_PL.QuadraticNominalPoint_L4,
    m_flow_nom=0.5,
    Delta_p_nom=1100,
    useHomotopy=true,
    showData=true,
    length=5000,
    diameter_i=0.3,
    T_start=ones(pipe_ClaraSimple.N_cv)*293.15,
    p_start=linspace(
        1593073.8073222376,
        1600000.0,
        pipe_ClaraSimple.N_cv)) annotation (Placement(transformation(extent={{-54,50},{-26,60}})));
//-------------------------------------------------------------------------------------------------------------
  Modelica.Blocks.Sources.CombiTimeTable Table(
    tableOnFile=false,
    table=[1,0.3; 2,0.3; 3,0.3; 4,0.3; 5,0.3; 6,0.3; 7,0.3; 8,0.05; 9,0.3; 10,0.3; 11,0.3; 12,10; 13,0.3; 14,0.3; 15,0.3],
    tableName="tab3",
    startTime=10)    annotation (Placement(transformation(
extent={{10,-10},{-10,10}},
origin={96,-16})));
  Modelica.Blocks.Sources.CombiTimeTable Table1(
    tableOnFile=false,
    table=[1,-0.3; 2,-0.3; 3,-0.3; 4,-0.3; 5,-0.3; 6,-0.3; 7,-0.3; 8,-0.05; 9,-0.3; 10,-0.3; 11,-0.3; 12,-10; 13,-0.3; 14,-0.3; 15,-0.3],
    tableName="tab3",
    startTime=10)    annotation (Placement(transformation(
extent={{10,-10},{-10,10}},
origin={76,44})));

 // Gas_Init gas_Init(redeclare model PressureLoss = TransiEnt.Components.Gas.VolumesValvesFittings.Base.PhysicalPL_L4)                      annotation (Placement(transformation(extent={{-148,2},{-128,22}})));

equation
  connect(boundaryGas_pTxi.gas_a,pipe_ClaraAdvanced. inlet) annotation (Line(
      points={{-90,28},{-58,28}},
      color={118,106,98},
      thickness=0.5));
  connect(pipe_ClaraAdvanced.outlet,boundaryGas_Txim_flow. gas_a) annotation (Line(
      points={{-26,28},{20,28}},
      color={118,106,98},
      thickness=0.5));
  connect(Sink_at_2.m_flow, Table.y[1]) annotation (Line(points={{58.0744,-32.9957},{70,-32.9957},{70,-16},{85,-16}},
                                                                                                            color={0,0,127}));
  connect(Sink_at_1.m_flow, Table.y[1]) annotation (Line(points={{56.0744,7.00432},{72,7.00432},{72,-16},{85,-16}},       color={0,0,127}));
  connect(boundaryGas_pTxi1.gas_a, pipe_ClaraSimple.inlet) annotation (Line(
      points={{-94,54},{-94,55},{-54,55}},
      color={118,106,98},
      thickness=0.5));
  connect(pipe_ClaraSimple.outlet, boundaryGas_Txim_flow1.gas_a) annotation (Line(
      points={{-26,55},{-26,54},{16,54}},
      color={118,106,98},
      thickness=0.5));
  connect(Sink_at_2.gasPort, pipe.gasPortOut) annotation (Line(
      points={{35.256,-39.3723},{23.628,-39.3723},{23.628,-40},{12,-40}},
      color={255,255,0},
      thickness=1.5));
  connect(pipe.gasPortIn, boundary_pTxi2.gasPort) annotation (Line(
      points={{-16,-40},{-42,-40}},
      color={255,255,0},
      thickness=1.5));
  connect(pipe_advanced.gasPortIn, boundary_pTxi1.gasPort) annotation (Line(
      points={{-22,0},{-46,0}},
      color={255,255,0},
      thickness=1.5));
  connect(pipe_advanced.gasPortOut, Sink_at_1.gasPort) annotation (Line(
      points={{8,0},{33.256,0.6277}},
      color={255,255,0},
      thickness=1.5));
  connect(Table1.y[1], boundaryGas_Txim_flow1.m_flow) annotation (Line(points={{65,44},{42,44},{42,60},{36,60}}, color={0,0,127}));
  connect(boundaryGas_Txim_flow.m_flow, boundaryGas_Txim_flow1.m_flow) annotation (Line(points={{40,34},{42,34},{42,60},{36,60}}, color={0,0,127}));
  annotation (uses(ClaRa(version="1.7.0"), TransiEnt(version="2.0.1"),
      Modelica(version="4.0.0")));
end Test_Bench_Pipe;
