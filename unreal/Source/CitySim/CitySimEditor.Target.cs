using UnrealBuildTool;
using System.Collections.Generic;

public class CitySimEditorTarget : TargetRules
{
	public CitySimEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.V5;
		IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_4;
		ExtraModuleNames.AddRange(new string[] { "CitySim" });
	}
}

