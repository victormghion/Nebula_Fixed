// Copyright
using UnrealBuildTool;

public class CitySim : ModuleRules
{
	public CitySim(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"Json",
			"JsonUtilities",
			"InputCore",
			"DeveloperSettings",
			"MassEntity",
			"MassActors",
			"MassAIBehavior",
			"StructUtils",
			"DataRegistry",
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Projects",
		});
	}
}

