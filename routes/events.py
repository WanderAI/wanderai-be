from fastapi import APIRouter, Depends, HTTPException, Request, status
from models.events import Alamat, UpdateBensin
from services.auth import AuthHandler, JWTBearer
from services.database_manager import dbInstance
from services.urlhandler import mapsapi, daveroot
from sqlalchemy import text

event_router = APIRouter(
    tags=["Events"]
)

@event_router.get("/get-all-bensin")
def getAllBensin(Authorize: JWTBearer = Depends(JWTBearer())):
    pertamaxO = dbInstance.conn.execute(text("SELECT harga FROM bensin WHERE jenisBensin=:jenisBensin") , {"jenisBensin":"pertamax"})
    pertaliteO = dbInstance.conn.execute(text("SELECT harga FROM bensin WHERE jenisBensin=:jenisBensin") , {"jenisBensin":"pertalite"})
    solarO = dbInstance.conn.execute(text("SELECT harga FROM bensin WHERE jenisBensin=:jenisBensin") , {"jenisBensin":"solar"})
    
    for getterPertamax in pertamaxO:
        hargaPertamax = getterPertamax[0]
        
    for getterPertalite in pertaliteO:
        hargaPertalite = getterPertalite[0]

    for getterSolar in solarO:
        hargaSolar = getterSolar[0]
    
    return {"Pertamax": hargaPertamax, "Pertalite": hargaPertalite, "solar": hargaSolar}

def getAverageBensin():
    pertamaxO = dbInstance.conn.execute(text("SELECT harga FROM bensin WHERE jenisBensin=:jenisBensin") , {"jenisBensin":"pertamax"})
    pertaliteO = dbInstance.conn.execute(text("SELECT harga FROM bensin WHERE jenisBensin=:jenisBensin") , {"jenisBensin":"pertalite"})
    solarO = dbInstance.conn.execute(text("SELECT harga FROM bensin WHERE jenisBensin=:jenisBensin") , {"jenisBensin":"solar"})

    ## Tambahkan weighter menyesuaikan dengan jumlah pengguna jenis bensin
    weighterPertamax = 2
    weighterPertalite = 6
    weighterSolar = 1
    weighterTotal = weighterPertamax + weighterPertalite + weighterSolar

    for getterPertamax in pertamaxO:
        hargaPertamax = getterPertamax[0]
        
    for getterPertalite in pertaliteO:
        hargaPertalite = getterPertalite[0]

    for getterSolar in solarO:
        hargaSolar = getterSolar[0]

    hargaAverage = ((hargaPertamax*weighterPertamax) + (hargaPertalite*weighterPertalite) + (hargaSolar*weighterSolar))/weighterTotal
    return {"Harga rata-rata bensin": hargaAverage}
    
@event_router.put('/update-bensin', status_code=201)
def updateBensin(updateBensinParam: UpdateBensin, Authorize: JWTBearer = Depends(JWTBearer())):
    listJenisBensin = ['pertamax', 'pertalite', 'solar']
    
    if (updateBensinParam.hargaBaru < 1000):
        raise HTTPException(status_code=405, detail="Masukkan harga baru dengan benar!")
        return
    
    if (updateBensinParam.jenisBensin.lower() not in listJenisBensin):
        raise HTTPException(status_code=405, detail="Jenis bensin tidak terdaftar!")
        return

    newBensin = {"jenisBensin": updateBensinParam.jenisBensin.lower(), "hargaBaru": updateBensinParam.hargaBaru}

    query = text("UPDATE bensin SET jenisBensin = :jenisBensin, harga = :hargaBaru WHERE jenisBensin = :jenisBensin")

    try:
        dbInstance.conn.execute(query, newBensin)
        return {"message": "Harga Berhasil diperbarui!"}
    except:
        raise HTTPException(status_code=406, detail="Update gagal, silakan coba lagi!")

@event_router.post("/order")
def getPrice(alamatAwal: Alamat, alamatTujuan: Alamat, Authorize: JWTBearer = Depends(JWTBearer())):

    drivingDist = mapsapi()

    msg = drivingDist.getDrivingDistanceMaps(alamatAwal, alamatTujuan)

    distance = msg["rows"][0]["elements"][0]["distance"]["value"]
    seconds = msg["rows"][0]["elements"][0]["duration"]["value"]

    avg_speed = distance/seconds

    avg_speed_kmh = avg_speed * 3.6

    if avg_speed <= 3:
        eta = 1.5
    elif avg_speed <= 5:
        eta = 1.2
    else:
        eta = 1

    basicPrice = 4*(distance/3) + 4000
    
    efficiency = 40000
    hargaBensin = int(getAverageBensin()["Harga rata-rata bensin"])
    price = ((distance*hargaBensin*eta)/efficiency) + basicPrice
    newOrder = {"namaPengambil": alamatAwal.nama, "namaPenerima": alamatTujuan.nama, "jalanAwal": alamatAwal.jalan, "kotaAwal": alamatAwal.kota, "jalanTujuan": alamatTujuan.jalan, "kotaTujuan": alamatTujuan.kota, "price1": price}

    query = text("INSERT INTO orderkurirku (namaPengambil, namaPenerima, jalanAwal, kotaAwal, jalanTujuan, kotaTujuan, price) VALUES (:namaPengambil, :namaPenerima, :jalanAwal, :kotaAwal, :jalanTujuan, :kotaTujuan, :price1)")
    try:
        dbInstance.conn.execute(query, newOrder)
        return {"origin": msg["origin_addresses"][0],
            "destination": msg["destination_addresses"][0],
            "drivingDistanceMeters": distance,
            "drivingTimeSeconds": seconds,
            "avgSpeedKmh": avg_speed_kmh,
            "priceRupiah": price,
            "message": "order berhasil dibuat!"
    }
    except:
        raise HTTPException(status_code=406, detail="Order gagal, silakan coba lagi")


@event_router.post("/get-price")
def getPrice(alamatAwal: Alamat, alamatTujuan: Alamat):
    drivingDist = mapsapi()
    msg = drivingDist.getDrivingDistanceMaps(alamatAwal, alamatTujuan)

    distance = msg["rows"][0]["elements"][0]["distance"]["value"]
    seconds = msg["rows"][0]["elements"][0]["duration"]["value"]

    avg_speed = distance/seconds

    avg_speed_kmh = avg_speed * 3.6

    if avg_speed <= 3:
        eta = 1.5
    elif avg_speed <= 5:
        eta = 1.2
    else:
        eta = 1

    basicPrice = 4*(distance/3)
    
    efficiency = 40000
    hargaBensin = int(getAverageBensin()["Harga rata-rata bensin"])
    price = ((distance*hargaBensin*eta)/efficiency) + basicPrice
    return {"alamatAsal": msg["origin_addresses"][0],
            "alamatTujuan": msg["destination_addresses"][0],
            "priceRupiah": price
    }

@event_router.get("/get-pemesan-shoetify")
def getAllBensin():
    dave = daveroot()
    msg = dave.getDaveRoot()
    return msg