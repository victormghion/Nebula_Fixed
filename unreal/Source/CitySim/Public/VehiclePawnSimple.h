#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/FloatingPawnMovement.h"
#include "VehiclePawnSimple.generated.h"

UCLASS(BlueprintType, Blueprintable)
class CITYSIM_API AVehiclePawnSimple : public APawn
{
	GENERATED_BODY()
public:
	AVehiclePawnSimple();
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TObjectPtr<UFloatingPawnMovement> Movement;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Vehicle")
	float ForwardSpeed = 600.f;
};


