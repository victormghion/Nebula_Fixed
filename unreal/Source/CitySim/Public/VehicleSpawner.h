#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VehicleSpawner.generated.h"

class ARoadNetworkActor;
class USplineComponent;

UCLASS(BlueprintType, Blueprintable)
class CITYSIM_API AVehicleSpawner : public AActor
{
	GENERATED_BODY()
public:
	AVehicleSpawner();
	virtual void BeginPlay() override;

	UPROPERTY(EditAnywhere, Category="Spawning")
	TSubclassOf<APawn> VehicleClass;

	UPROPERTY(EditAnywhere, Category="Spawning")
	int32 MaxVehicles = 50;

	UPROPERTY(EditAnywhere, Category="Spawning")
	TObjectPtr<ARoadNetworkActor> RoadNetwork;

protected:
	void SpawnOnSplines();
};


