#include "RoadNetworkActor.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

ARoadNetworkActor::ARoadNetworkActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ARoadNetworkActor::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	TArray<FGraphNode> Nodes;
	TArray<FGraphEdge> Edges;
	if (LoadGraph(Nodes, Edges))
	{
		BuildSplines(Nodes, Edges);
	}
}

void ARoadNetworkActor::ClearExisting()
{
	TArray<UActorComponent*> Existing = GetComponentsByClass(USplineComponent::StaticClass());
	for (UActorComponent* C : Existing)
	{
		C->DestroyComponent();
	}
	RoadSplines.Empty();
}

bool ARoadNetworkActor::LoadGraph(TArray<FGraphNode>& OutNodes, TArray<FGraphEdge>& OutEdges) const
{
	if (LanesGraphJson.FilePath.IsEmpty()) return false;
	const FString AbsPath = FPaths::ConvertRelativePathToFull(LanesGraphJson.FilePath);
	FString JsonText;
	if (!FFileHelper::LoadFileToString(JsonText, *AbsPath))
	{
		return false;
	}
	TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
	TSharedPtr<FJsonObject> Root;
	if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
	{
		return false;
	}
	const TArray<TSharedPtr<FJsonValue>>* NodesJson;
	const TArray<TSharedPtr<FJsonValue>>* EdgesJson;
	if (!Root->TryGetArrayField(TEXT("nodes"), NodesJson) || !Root->TryGetArrayField(TEXT("edges"), EdgesJson))
	{
		return false;
	}
	OutNodes.Reserve(NodesJson->Num());
	for (const TSharedPtr<FJsonValue>& V : *NodesJson)
	{
		TSharedPtr<FJsonObject> Obj = V->AsObject();
		if (!Obj) continue;
		FGraphNode N;
		N.Id = Obj->GetIntegerField(TEXT("id"));
		const double X = Obj->GetNumberField(TEXT("x"));
		const double Y = Obj->GetNumberField(TEXT("y"));
		const double Z = Obj->HasTypedField<EJson::Number>(TEXT("z")) ? Obj->GetNumberField(TEXT("z")) : 0.0;
		// Convert meters to centimeters and swap Y to Unreal's left-handed Y
		N.Position = FVector(Z * WorldScale, Y * WorldScale, X * WorldScale); // If needed, adjust axis mapping
		OutNodes.Add(N);
	}
	OutEdges.Reserve(EdgesJson->Num());
	for (const TSharedPtr<FJsonValue>& V : *EdgesJson)
	{
		TSharedPtr<FJsonObject> Obj = V->AsObject();
		if (!Obj) continue;
		FGraphEdge E;
		E.From = Obj->GetIntegerField(TEXT("from"));
		E.To = Obj->GetIntegerField(TEXT("to"));
		E.LengthM = Obj->HasField(TEXT("length_m")) ? Obj->GetNumberField(TEXT("length_m")) : 0.0;
		E.SpeedKph = Obj->HasField(TEXT("speed_kph")) ? Obj->GetNumberField(TEXT("speed_kph")) : 40.0;
		E.Lanes = Obj->HasField(TEXT("lanes")) ? Obj->GetIntegerField(TEXT("lanes")) : 1;
		E.bOneway = Obj->HasField(TEXT("oneway")) ? Obj->GetBoolField(TEXT("oneway")) : true;
		OutEdges.Add(E);
	}
	return true;
}

void ARoadNetworkActor::BuildSplines(const TArray<FGraphNode>& Nodes, const TArray<FGraphEdge>& Edges)
{
	ClearExisting();
	TMap<int32, FVector> NodeIdToPos;
	for (const FGraphNode& N : Nodes)
	{
		NodeIdToPos.Add(N.Id, N.Position);
	}
	for (const FGraphEdge& E : Edges)
	{
		const FVector* FromPos = NodeIdToPos.Find(E.From);
		const FVector* ToPos = NodeIdToPos.Find(E.To);
		if (!FromPos || !ToPos) continue;
		USplineComponent* Spline = NewObject<USplineComponent>(this);
		Spline->RegisterComponent();
		Spline->SetMobility(EComponentMobility::Static);
		Spline->ClearSplinePoints(false);
		Spline->AddSplinePoint(*FromPos, ESplineCoordinateSpace::World, false);
		Spline->AddSplinePoint(*ToPos, ESplineCoordinateSpace::World, false);
		Spline->SetClosedLoop(false);
		Spline->UpdateSpline();
		Spline->AttachToComponent(GetRootComponent() ? GetRootComponent() : (USceneComponent*)this->GetComponentByClass(USceneComponent::StaticClass()), FAttachmentTransformRules::KeepWorldTransform);
		RoadSplines.Add(Spline);
		// If not oneway, we can create the reverse edge as another spline
		if (!E.bOneway)
		{
			USplineComponent* RSpline = NewObject<USplineComponent>(this);
			RSpline->RegisterComponent();
			RSpline->SetMobility(EComponentMobility::Static);
			RSpline->ClearSplinePoints(false);
			RSpline->AddSplinePoint(*ToPos, ESplineCoordinateSpace::World, false);
			RSpline->AddSplinePoint(*FromPos, ESplineCoordinateSpace::World, false);
			RSpline->SetClosedLoop(false);
			RSpline->UpdateSpline();
			RSpline->AttachToComponent(GetRootComponent() ? GetRootComponent() : (USceneComponent*)this->GetComponentByClass(USceneComponent::StaticClass()), FAttachmentTransformRules::KeepWorldTransform);
			RoadSplines.Add(RSpline);
		}
	}
}


