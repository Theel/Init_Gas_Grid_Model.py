within ;
model PipeFlow_L4_Advanced "A 1D tube-shaped control volume considering heat transfer in a straight pipe with dynamic momentum balance and simple energy balance."

  extends VolumeRealGas_L4_advanced_V1(
    redeclare model Geometry =
        ClaRa.Basics.ControlVolumes.Fundamentals.Geometry.PipeGeometry_N_cv (
        z_in=z_in,
        z_out=z_out,
        N_tubes=N_tubes,
        N_cv=N_cv,
        diameter=diameter_i,
        length=length,
        Delta_x=Delta_x));

  extends ClaRa.Basics.Icons.Pipe_L4_a;
  extends ClaRa.Basics.Icons.ComplexityLevel(complexity="L4");
  ClaRa.Basics.Interfaces.Connected2SimCenter connected2SimCenter(
    powerIn=noEvent(if sum(heat.Q_flow) > 0 then sum(heat.Q_flow) else 0),
    powerOut_th=if not heatFlowIsLoss then -sum(heat.Q_flow) else 0,
    powerOut_elMech=0,
    powerAux=0)  if contributeToCycleSummary;

//## P A R A M E T E R S #######################################################################################

//____Geometric data_____________________________________________________________________________________
public
  parameter ClaRa.Basics.Units.Length length=1 "|Geometry|Length of the pipe";
  parameter ClaRa.Basics.Units.Length diameter_i=0.1 "|Geometry|Inner diameter of the pipe";
  parameter ClaRa.Basics.Units.Length z_in=0.1 "Height of inlet above ground" annotation (Dialog(group="Geometry"));
  parameter ClaRa.Basics.Units.Length z_out=0.1 "Height of outlet above ground" annotation (Dialog(group="Geometry"));


  parameter Integer N_tubes= 1 "Number Of parallel pipes"
                                                         annotation(Dialog(group="Geometry"));
  parameter Integer N_passes=1 "Number of passes of the tubes" annotation(Dialog(group="Geometry"));
  parameter Integer orientation=0 "Main orientation of tube bundle (N_passes>1)" annotation(Dialog(group="Geometry", enable=(N_passes>1)), choices(choice = 0 "Horizontal", choice = 1 "Vertical"));

//____Discretisation_____________________________________________________________________________________
    parameter Integer N_cv(min=3)=3 "|Discretisation|Number of finite volumes";
public
  inner parameter ClaRa.Basics.Units.Length Delta_x[N_cv]=ClaRa.Basics.Functions.GenerateGrid(
      {0},
      length,
      N_cv) "|Discretisation|Discretisation scheme";

//________Summary_________________
  parameter Boolean contributeToCycleSummary = simCenter.contributeToCycleSummary "True if component shall contribute to automatic efficiency calculation"
                                                                                            annotation(Dialog(tab="Summary and Visualisation"));
  parameter Boolean heatFlowIsLoss = true "True if negative heat flow is a loss (not a process product)" annotation(Dialog(tab="Summary and Visualisation"));

  // _____________________________________________
  //
  //                 Outer Models
  // _____________________________________________

  outer TransiEnt.ModelStatistics modelStatistics;

    // _____________________________________________
  //
  //           Instances of other Classes
  // _____________________________________________
  replaceable model CostSpecsGeneral = TransiEnt.Components.Statistics.ConfigurationData.GeneralCostSpecs.Empty constrainedby TransiEnt.Components.Statistics.ConfigurationData.GeneralCostSpecs.PartialCostSpecs
                                                                                                                                                                                 "Cost model" annotation(Dialog(group="Statistics"),choicesAllMatching);

  TransiEnt.Components.Statistics.Collectors.LocalCollectors.CollectCostsGeneral collectCosts(
    der_E_n=0,
    E_n=0,
    redeclare model CostRecordGeneral = CostSpecsGeneral (size1=diameter_i, size2=length*N_tubes),
    produces_P_el=false,
    consumes_P_el=false,
    produces_Q_flow=false,
    consumes_Q_flow=false,
    produces_H_flow=false,
    consumes_H_flow=false,
    produces_other_flow=false,
    consumes_other_flow=false,
    produces_m_flow_CDE=false,
    consumes_m_flow_CDE=false) annotation (Placement(transformation(extent={{-140,-50},{-120,-30}})));


//### E Q U A T I O N P A R T #######################################################################################
//-------------------------------------------
equation

  assert(abs(z_out-z_in) <= length, "Length of pipe less than vertical height", AssertionLevel.error);
  assert(not (N_cv==1 and not frictionAtInlet and not frictionAtOutlet), "N_cv==1 and not frictionAtInlet and not frictionAtOutlet in " + getInstanceName());
  connect(modelStatistics.costsCollector, collectCosts.costsCollector);
annotation (defaultComponentName="pipe",Icon(graphics={
        Polygon(
          points={{-132,42},{-122,42},{-114,34},{-114,-36},{-122,-42},{-132,-42},
              {-132,42}},
          pattern=LinePattern.None,
          smooth=Smooth.None,
          fillColor= {0,131,169},
          fillPattern=FillPattern.Solid,
          visible=frictionAtInlet),
        Polygon(
          points={{132,42},{122,42},{114,34},{114,-36},{122,-42},{132,-42},
              {132,42}},
          pattern=LinePattern.None,
          smooth=Smooth.None,
          fillColor= {0,131,169},
          fillPattern=FillPattern.Solid,
          visible=frictionAtOutlet)},        coordinateSystem(preserveAspectRatio=false,
                                                           extent={{-140,-60},{
            140,60}})),
        Diagram(graphics,
                coordinateSystem(preserveAspectRatio=false,
          extent={{-140,-60},{140,60}})));
end PipeFlow_L4_Advanced;
