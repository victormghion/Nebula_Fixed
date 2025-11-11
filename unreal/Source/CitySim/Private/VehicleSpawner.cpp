#include "VehicleSpawner.h"
#include "RoadNetworkActor.h"
#include "Components/SplineComponent.h"
#include "Kismet/KismetMathLibrary.h"

AVehicleSpawner::AVehicleSpawner()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AVehicleSpawner::BeginPlay()
{
	Super::BeginPlay();
	SpawnOnSplines();
}

void AVehicleSpawner::SpawnOnSplines()
{
	if (!VehicleClass || !RoadNetwork) return;
	const TArray<USplineComponent*>& Splines = RoadNetwork->GetRoadSplines();
	if (Splines.Num() == 0) return;

	int32 Spawned = 0;
	for (int32 i = 0; i < Splines.Num() && Spawned < MaxVehicles; ++i)
	{
		USplineComponent* S = Splines[i];
		if (!S) continue;
		const float Len = S->GetSplineLength();
		const float Dist = UKismetMathLibrary::RandomFloatInRange(0.f, Len);
		const FVector Location = S->GetLocationAtDistanceAlongSpline(Dist, ESplineCoordinateSpace::World);
		const FRotator Rotation = S->GetRotationAtDistanceAlongSpline(Dist, ESplineCoordinateSpace::World);
		GetWorld()->SpawnActor<APawn>(VehicleClass, Location, Rotation);
		Spawned++;
	}
}


