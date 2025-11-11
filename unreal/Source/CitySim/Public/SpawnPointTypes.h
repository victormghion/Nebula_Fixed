#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "SpawnPointTypes.generated.h"

USTRUCT(BlueprintType)
struct FSpawnPointRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float X = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float Y = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float Z = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName SpawnTag;
};


