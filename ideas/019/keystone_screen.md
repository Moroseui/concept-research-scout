# Keystone screen

## Keystone as stated

> Routine CT-RATE resolution and CT-CLIP preprocessing preserve enough wall completeness and cyst adjacency to distinguish honeycombing topology from paraseptal emphysema and traction bronchiolectasis without human labels.

This is the load-bearing fact. It is not enough that CT-RATE contains chest CT, that metadata include voxel spacing, or that honeycombing has a clinical definition. The proposed measurement must remain separable from its two named mimics after the exact released preprocessing.

## What I inspected

I inspected the official CT-CLIP repository at commit `a2a155c601987820433c01db69b64d701d3d229d`, specifically the training loader and the training configuration.

The loader reads per-volume spacing and fixes the model-space resolution:

> `xy_spacing = float(row["XYSpacing"].iloc[0][1:][:-2].split(",")[0])`  
> `z_spacing = float(row["ZSpacing"].iloc[0])`

and then:

> `target_x_spacing = 0.75`  
> `target_y_spacing = 0.75`  
> `target_z_spacing = 1.5`

Source: [official CT-CLIP `scripts/data.py`, lines 96–109, commit `a2a155c`](https://github.com/ibrahimethemhamamci/CT-CLIP/blob/a2a155c601987820433c01db69b64d701d3d229d/scripts/data.py#L96-L109).

Resampling is trilinear:

> `resized_array = F.interpolate(array, size=new_shape, mode='trilinear', align_corners=False).cpu().numpy()`

Source: [official CT-CLIP `scripts/data.py`, lines 27–34, commit `a2a155c`](https://github.com/ibrahimethemhamamci/CT-CLIP/blob/a2a155c601987820433c01db69b64d701d3d229d/scripts/data.py#L27-L34).

The resampled tensor is forced to a fixed field of view:

> `target_shape = (480,480,240)`

followed by center cropping and constant-value padding:

> `tensor = tensor[h_start:h_end, w_start:w_end, d_start:d_end]`  
> `tensor = torch.nn.functional.pad(tensor, (pad_d_before, pad_d_after, pad_w_before, pad_w_after, pad_h_before, pad_h_after), value=-1)`

Source: [official CT-CLIP `scripts/data.py`, lines 128–156, commit `a2a155c`](https://github.com/ibrahimethemhamamci/CT-CLIP/blob/a2a155c601987820433c01db69b64d701d3d229d/scripts/data.py#L128-L156).

Finally, the released training configuration uses relatively coarse encoder patches:

> `image_size = 480,`  
> `patch_size = 20,`  
> `temporal_patch_size = 10,`

Source: [official CT-CLIP `scripts/run_train.py`, lines 17–26, commit `a2a155c`](https://github.com/ibrahimethemhamamci/CT-CLIP/blob/a2a155c601987820433c01db69b64d701d3d229d/scripts/run_train.py#L17-L26).

Thus the input tensor has nominal 0.75 × 0.75 × 1.5 mm sampling, while one first-stage token spans 15 × 15 × 15 mm. The latter does **not** by itself prove destruction of smaller structures: the learned linear patch embedding receives the constituent voxel values. Conversely, neither the loader nor the architecture demonstrates preservation of complete cyst walls, multilayer adjacency, or separability from paraseptal emphysema and traction bronchiolectasis.

I also inspected the official CT-RATE release page. It says access to the image files requires acceptance of the dataset terms:

> “This repository is publicly accessible, but you have to accept the conditions to access its files and content.”

Source: [official CT-RATE repository, gated-dataset notice](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE/tree/main).

No representative native volumes, corresponding final tensors, or topology/mimic separability results were available in the repository checkout. Therefore the actual preservation claim could not be directly tested in this screen.

## Residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

The nearest checkable facts are that physical-spacing metadata are read, volumes are resampled to a fixed nominal spacing, and the encoder consumes fixed-size patches. The card is still assuming that these operations preserve the wall closure and adjacency needed by its deterministic topology measure **and** that the resulting measure distinguishes honeycombing from the two named mimics on CT-RATE. That assumption is load-bearing and is the same as the stated keystone, not a different hidden keystone.

The quoted source code neither verifies nor falsifies that assumption. Verification requires the proposed native-to-final-tensor audit on actual CT-RATE cases, with an annotation-independent or otherwise defensible reference for mimic separability. Accordingly, the honest screen result is `UNVERIFIABLE`, not `PASS` and not `KILL`.

```json
{"verdict": "UNVERIFIABLE", "evidence": "resized_array = F.interpolate(array, size=new_shape, mode='trilinear', align_corners=False).cpu().numpy()", "source": "https://github.com/ibrahimethemhamamci/CT-CLIP/blob/a2a155c601987820433c01db69b64d701d3d229d/scripts/data.py#L27-L34", "note": "The exact preprocessing is inspected, but only an audit on actual native and final tensors can establish preservation and mimic separability."}
```
