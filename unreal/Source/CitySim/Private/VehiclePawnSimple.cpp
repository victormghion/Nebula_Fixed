#include "VehiclePawnSimple.h"
#include "Components/CapsuleComponent.h"

AVehiclePawnSimple::AVehiclePawnSimple()
{
	PrimaryActorTick.bCanEverTick = true;
	AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
	Movement = CreateDefaultSubobject<UFloatingPawnMovement>(TEXT("Movement"));
	Movement->SetPlaneConstraintEnabled(false);
}

void AVehiclePawnSimple::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	AddMovementInput(GetActorForwardVector(), ForwardSpeed * DeltaSeconds);
}


