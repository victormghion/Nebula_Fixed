#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Engine/DataTable.h"
#include "SpawnPointTypes.h"
#include "SpawnManager.generated.h"

UCLASS(BlueprintType, Blueprintable)
class CITYSIM_API ASpawnManager : public AActor
{
	GENERATED_BODY()

public:
	ASpawnManager();
	virtual void BeginPlay() override;

protected:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Spawning")
	TObjectPtr<UDataTable> SpawnPointsTable;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Spawning")
	TSubclassOf<AActor> PedestrianActorClass;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Spawning")
	int32 MaxSpawnCount = 300;

private:
	void SpawnFromDataTable();
};


