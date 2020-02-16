Concepts
========

Tracker
-------

One important concept of the Station is a so-called `Tracker`.
Imagine that the Station sees the container images in the remote registry as
objects in the distance floating by. It is important to understand that from the viewpoint
of the Station, these images are transient, which implies that at any given point in time:

* New images might appear
* Previous images disappear
* A previous image is effectively overwritten by another one, hence changing the identity

The Station is interested in some images (since they might be somehow related to PHT images, such as baseimages) but
might not care about other images. 

This is where Tracker come into play. A Tracker selects an image (via the repository and tag) and keeps track of its identites, hence the
name. A tracker can have multiple identities, which are ordered by their time of creation, called the revision.

TODO: figure
   

The combination (tuple) of ``docker_image_manifest_id`` and ``docker_image_config_id`` constitutes the identity,

