#include "SpawnManager.h"
#include "Engine/World.h"
#include "Kismet/KismetMathLibrary.h"

ASpawnManager::ASpawnManager()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ASpawnManager::BeginPlay()
{
	Super::BeginPlay();
	SpawnFromDataTable();
}

void ASpawnManager::SpawnFromDataTable()
{
	if (!SpawnPointsTable || !PedestrianActorClass)
	{
		return;
	}

	TArray<FName> RowNames = SpawnPointsTable->GetRowNames();
	int32 Spawned = 0;
	for (const FName& RowName : RowNames)
	{
		if (Spawned >= MaxSpawnCount)
		{
			break;
		}
		const FSpawnPointRow* Row = SpawnPointsTable->FindRow<FSpawnPointRow>(RowName, TEXT("Spawn"));
		if (!Row)
		{
			continue;
		}
		const FVector Location(Row->X, Row->Y, Row->Z);
		const FRotator Rotation(0.f, UKismetMathLibrary::RandomFloatInRange(0.f, 360.f), 0.f);
		GetWorld()->SpawnActor<AActor>(PedestrianActorClass, Location, Rotation);
		Spawned++;
	}
}


